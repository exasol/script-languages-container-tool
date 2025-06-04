import asyncio
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiohttp
from tqdm import tqdm

DOCKERHUB_API = "https://hub.docker.com/v2"


class TooManyRequestsError(Exception):
    """Raised when a 429 Too Many Requests is returned by Docker Hub."""


@dataclass
class Tag:
    name: str
    date: datetime
    deleted: bool


async def get_jwt_token(
    session: aiohttp.ClientSession, username: str, password: str
) -> str:
    """
    Log in to Docker Hub and retrieve a JWT token.
    """
    login_url = f"{DOCKERHUB_API}/users/login/"
    payload = {"username": username, "password": password}

    async with session.post(login_url, json=payload) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data["token"]


def parse_iso_datetime(dt_str: str) -> datetime:
    """
    Parse an ISO8601 datetime string (with optional 'Z') into a timezone-aware datetime.
    """
    if dt_str.endswith("Z"):
        dt_str = dt_str[:-1]
    # remove microseconds as datetime.fromisoformat() always expects a fixed number of digits of microseconds,
    # whereas the ISO string from Dockerhub returns an arbitrary number of digits.
    pattern = re.compile(r"\.\d+$")
    dt_str = pattern.sub("", dt_str)
    return datetime.fromisoformat(dt_str)


async def fetch_old_tags(
    session: aiohttp.ClientSession,
    namespace: str,
    repo: str,
    threshold: datetime,
    token: str,
    max_number_of_pages: int,
) -> list[Tag]:
    """
    Fetch all tags for a repository, handling pagination.
    Returns a list of `Tag` objects.
    """
    tags: list[Tag] = []
    page = 1
    page_size = 100

    max_tags = page_size * max_number_of_pages

    while True:
        print(f"Fetching page {page} ...")
        url = (
            f"{DOCKERHUB_API}/repositories/"
            f"{namespace}/{repo}/tags?page={page}&page_size={page_size}"
        )
        headers = {"Authorization": f"JWT {token}"}
        async with session.get(url, headers=headers) as resp:
            if resp.status == 429:
                print("Ran into rate limit.")
                # If we run into rate limit here, we process all the tags which we fetched until now.
                break
            resp.raise_for_status()
            data = await resp.json()

        results = data.get("results", [])
        if not results:
            break

        for t in results:
            # Filter tags older than threshold
            updated = parse_iso_datetime(t["last_updated"])
            if updated < threshold:
                tags.append(Tag(name=t["name"], date=updated, deleted=False))

        if not data.get("next"):
            break

        page += 1

        if 0 < max_tags <= len(tags):
            break

    return tags


async def delete_tag(
    session: aiohttp.ClientSession,
    namespace: str,
    repo: str,
    tag: Tag,
    token: str,
    semaphore: asyncio.Semaphore,
) -> int:
    """
    Delete a single tag from the repository.
    If a 429 code is returned by Docker Hub, a TooManyRequestsError is raised.
    Otherwise, the status code is returned.
    """
    url = f"{DOCKERHUB_API}/repositories/{namespace}/{repo}/tags/{tag.name}/"
    headers = {"Authorization": f"JWT {token}"}

    async with semaphore:
        async with session.delete(url, headers=headers) as resp:
            if resp.status == 204:
                tag.deleted = True
            elif resp.status == 429:
                # Rate limit hit
                raise TooManyRequestsError(f"{namespace}/{repo}:{tag}")
            return resp.status


async def get_old_tags(
    namespace: str,
    repo: str,
    token: str,
    min_age_in_days: int,
    max_number_of_pages: int,
) -> list[Tag]:
    """
    Calculates the time threshold, opens a aiohttp.ClientSession session and then calls `fetch_old_tags`.
    """
    threshold = datetime.now() - timedelta(days=min_age_in_days)

    conn = aiohttp.TCPConnector(limit_per_host=10)
    async with aiohttp.ClientSession(connector=conn) as session:
        # 2) Fetch all tags
        print(f"Fetching tags for {namespace}/{repo} ...")
        old_tags = await fetch_old_tags(
            session, namespace, repo, threshold, token, max_number_of_pages
        )
        print(f"Total tags fetched: {len(old_tags)}")
        return old_tags


async def delete_tags(
    namespace: str,
    repo: str,
    token: str,
    tags_to_delete: list[Tag],
) -> bool:
    """
    Delete given tags from a repository, always with 3 Http requests in parallel.
    The method creates an aiohttp.ClientSession session, then creates all async delete tasks.
    Whenever one tasks raises the TooManyRequestsError exception, all other tasks are cancelled,
    and the method returns True. If no such exception is raised, the method returns False.
    """

    # Values higher will run deletion faster, but have higher risk of getting a 429,
    # see https://docs.docker.com/docker-hub/usage/#abuse-rate-limit
    sem = asyncio.Semaphore(2)

    retry = False
    conn = aiohttp.TCPConnector(limit_per_host=10)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            tasks = [
                asyncio.create_task(
                    delete_tag(session, namespace, repo, tag, token, sem)
                )
                for tag in tags_to_delete
            ]

            status_counter_map: dict[int, int] = {}
            retry = False

            for delete_coro in tqdm(
                asyncio.as_completed(tasks),
                total=len(tasks),
                desc="Deleting old tags",
            ):
                try:
                    status = await delete_coro
                    status_counter_map[status] = status_counter_map.get(status, 0) + 1
                except TooManyRequestsError as e:
                    # upon 429, cancel all pending tasks
                    retry = True
                    for t in tasks:
                        if not t.done():
                            t.cancel()
                    break

        finally:
            # ensure all tasks are concluded to suppress warnings
            await asyncio.gather(*tasks, return_exceptions=True)

        print(
            f"Deletion run completed. \n Status counters: \n {status_counter_map}\n Retry: {retry}",
        )
    return retry


async def clean_dockerhub(
    docker_repository: str,
    docker_username: str,
    docker_password: str,
    min_age_in_days: int,
    max_number_of_pages: int,
) -> None:
    """
    Cleans all tags in a Docker repository which are older than `min_age_in_days` days.
    1. Gets the auth token from Docker Hub.
    2. Fetches tags from Docker Hub (max. 10.000)
    3. Deletes the tags in a loop until all tags are deleted, or only errors != 429 were raised.
    """

    namespace, repo = docker_repository.split("/")

    # 1) Authenticate
    async with aiohttp.ClientSession() as session:

        token = await get_jwt_token(session, docker_username, docker_password)
        print("Authenticated successfully.")

    # 1) Fetch old tags
    old_tags = await get_old_tags(
        namespace, repo, token, min_age_in_days, max_number_of_pages
    )
    if not old_tags:
        print("No tags to delete. Exiting.")
        return

    # 2) Delete old tags. Repeat until we don't run into a rate limit
    while True:
        tags_to_delete = [tag for tag in old_tags if not tag.deleted]
        retry = await delete_tags(namespace, repo, token, tags_to_delete)
        if retry:
            for i in tqdm(range(60), "Waiting for rate limit."):
                time.sleep(1)
        else:
            break


def call_clean_dockerhub(
    docker_repository: str,
    docker_username: str,
    docker_password: str,
    min_age_in_days: int,
    max_number_of_pages: int,
):
    asyncio.run(
        clean_dockerhub(
            docker_repository,
            docker_username,
            docker_password,
            min_age_in_days,
            max_number_of_pages,
        )
    )

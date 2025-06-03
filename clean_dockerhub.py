import asyncio
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

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
    pattern = re.compile(r"\.\d+$")
    dt_str = pattern.sub("", dt_str)
    return datetime.fromisoformat(dt_str)


async def fetch_old_tags(
    session: aiohttp.ClientSession, namespace: str, repo: str, threshold: datetime
) -> list:
    """
    Fetch all tags for a repository, handling pagination.
    Returns a list of dicts with fields: 'name' and 'last_updated'.
    """
    tags: list[Tag] = []
    page = 1
    page_size = 100
    max_tags = (
        page_size * 10
    )  # Need to define max tags, otherwise will run into rate limit

    while True:
        print(f"Fetching page {page} ...")
        url = (
            f"{DOCKERHUB_API}/repositories/"
            f"{namespace}/{repo}/tags?page={page}&page_size={page_size}"
        )
        async with session.get(url) as resp:
            if resp.status == 429:
                print("Ran into rate limit.")
                break
            resp.raise_for_status()
            data = await resp.json()

        results = data.get("results", [])
        if not results:
            break

        for t in results:
            # 3) Filter tags older than threshold
            updated = parse_iso_datetime(t["last_updated"])
            if updated < threshold:
                tags.append(Tag(name=t["name"], date=updated, deleted=False))

        if not data.get("next"):
            break

        page += 1

        if len(tags) >= max_tags:
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


async def main(
    docker_repository: str,
    docker_username: str,
    docker_password: str,
    min_age_in_days: int,
) -> None:

    threshold = datetime.now() - timedelta(days=min_age_in_days)

    conn = aiohttp.TCPConnector(limit_per_host=10)
    async with aiohttp.ClientSession(connector=conn) as session:
        # 1) Authenticate
        token = await get_jwt_token(session, docker_username, docker_password)
        print("Authenticated successfully.")

        # 2) Fetch all tags
        print(f"Fetching tags for {docker_repository}...")
        namespace, repo = docker_repository.split("/")
        old_tags = await fetch_old_tags(session, namespace, repo, threshold)
        print(f"Total tags fetched: {len(old_tags)}")

        if not old_tags:
            print("No tags to delete. Exiting.")
            return

    # new code with tqdm progress bar
    sem = asyncio.Semaphore(5)  # or whatever concurrency limit you prefer

    tags_to_delete = old_tags
    retry = True
    while len(tags_to_delete) > 0 and retry:
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
                        status_counter_map[status] = (
                            status_counter_map.get(status, 0) + 1
                        )
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
        print("Deletion run completed. \n Status counters: \n", status_counter_map)
        tags_to_delete = [tag for tag in old_tags if not tag.deleted]
        if retry:
            for i in tqdm(range(60), "Waiting for rate limit."):
                time.sleep(1)


def call_clean_dockerhub(
    docker_repository: str,
    docker_username: str,
    docker_password: str,
    min_age_in_days: int,
):
    asyncio.run(
        main(docker_repository, docker_username, docker_password, min_age_in_days)
    )

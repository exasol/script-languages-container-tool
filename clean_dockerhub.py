import asyncio
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from http import HTTPStatus
from inspect import cleandoc

import aiohttp
from rich.console import Console
from tqdm import tqdm

DOCKERHUB_API = "https://hub.docker.com/v2"
LIMIT_SIMULTANEOUS_CONNECTIONS_TO_SAME_ENDPOINT = 10
"""
The value of this constant will be used for parameter `limit_per_host` during instantiation of class
https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.TCPConnector
"""

PAGE_SIZE = 100
"""
Page size when fetching existing tags from Dockhub Rest API.
According to https://docs.docker.com/reference/api/hub/latest/#tag/repositories/paths/~1v2~1namespaces~1%7Bnamespace%7D~1repositories~1%7Brepository%7D~1tags/get
the maximum value is 100.
"""


@dataclass(frozen=True)
class Context:
    docker_repository: str
    docker_username: str
    docker_password: str
    min_age_in_days: int
    max_number_tags: int

    @property
    def repository_url(self):
        return f"{DOCKERHUB_API}/repositories/{self.docker_repository}"


class TooManyRequestsError(Exception):
    """Raised when Docker Hub returned HTTP 429 Too Many Requests."""


@dataclass
class Tag:
    """
    Represents a specific tag of a docker image on Docker Hub.
    """

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
    Parse an ISO8601 datetime string (with optional suffix 'Z') into a
    timezone-aware datetime.
    """

    def remove_timezone(dt_str: str) -> str:
        return dt_str[:-1] if dt_str.endswith("Z") else dt_str

    def remove_microseconds(dt_str: str) -> str:
        """
        datetime.fromisoformat() always expects a fixed number of digits of microseconds,
        whereas the ISO string from Dockerhub returns an arbitrary number of digits.
        """
        return re.sub(r"\.\d+$", "", dt_str)

    normalized = remove_microseconds(remove_timezone(dt_str))
    return datetime.fromisoformat(normalized)


async def fetch_old_tags(
    session: aiohttp.ClientSession,
    context: Context,
    threshold: datetime,
    token: str,
) -> list[Tag]:
    """
    Fetch all tags for a repository on Docker Hub, handling pagination.
    Returns a list of `Tag` objects.
    """
    tags: list[Tag] = []
    page = 1

    console = Console()
    status_msg = f"Fetching pages for {context.docker_repository}...{{n_pages}} pages."
    with console.status(status_msg.format(n_pages=page)) as status:
        while True:
            url = f"{context.repository_url}/tags?page={page}&page_size={PAGE_SIZE}"

            headers = {"Authorization": f"JWT {token}"}
            async with session.get(url, headers=headers) as resp:
                if resp.status == HTTPStatus.TOO_MANY_REQUESTS.value:
                    console.log("[bold yellow]Ran into rate limit.")
                    # If observing a rate limit, then simply process only the tags fetched until now.
                    break
                resp.raise_for_status()
                data = await resp.json()

            results = data.get("results", [])
            if not results:
                break

            tags.extend(
                [
                    Tag(name=t["name"], date=t["last_updated"], deleted=False)
                    for t in results
                    if parse_iso_datetime(t["last_updated"]) < threshold
                ]
            )

            if not data.get("next"):
                break

            page += 1
            status.update(status_msg.format(n_pages=page))

            if 0 < context.max_number_tags <= len(tags):
                break
    console.log(f"[bold green]Total tags fetched: {len(tags)}")
    return tags


async def delete_tag(
    context: Context,
    session: aiohttp.ClientSession,
    tag: Tag,
    token: str,
    semaphore: asyncio.Semaphore,
) -> int:
    """
    Delete a single tag from the repository.
    Raises a TooManyRequestsError if Docker Hub returns HTTP 429.
    Otherwise, the status code is returned.
    """
    url = f"{context.repository_url}/tags/{tag.name}/"
    headers = {"Authorization": f"JWT {token}"}

    async with semaphore:
        async with session.delete(url, headers=headers) as resp:
            if resp.status == HTTPStatus.NO_CONTENT.value:
                tag.deleted = True
            elif resp.status == HTTPStatus.TOO_MANY_REQUESTS.value:
                # Rate limit hit
                raise TooManyRequestsError(f"{context.docker_repository}:{tag}")
            return resp.status


async def get_old_tags(
    context: Context,
    token: str,
) -> list[Tag]:
    """
    Calculates the time threshold, opens a aiohttp.ClientSession session and then calls `fetch_old_tags`.
    """
    threshold = datetime.now() - timedelta(days=context.min_age_in_days)

    conn = aiohttp.TCPConnector(
        limit_per_host=LIMIT_SIMULTANEOUS_CONNECTIONS_TO_SAME_ENDPOINT
    )
    async with aiohttp.ClientSession(connector=conn) as session:
        old_tags = await fetch_old_tags(session, context, threshold, token)
        return old_tags


async def delete_tags(
    context: Context,
    token: str,
    tags_to_delete: list[Tag],
) -> bool:
    """
    Delete the specified tags from a repository on Docker Hub. Use multiple HTTP
    requests in parallel, see constant PARALLEL_TASKS.

    The method creates an aiohttp.ClientSession session and an async delete task
    for each tag to delete.

    The methods's boolean return value indicates whether a retry is required.
    If none of the delete tasks raises a TooManyRequestsError exception then
    the method returns needs_retry=False.

    In case of any of the delete tasks raising this exception then the method
    returns needs_retry=True.
    """

    # More parallel tasks will run deletion faster, but have higher risk of getting a 429,
    # see https://docs.docker.com/docker-hub/usage/#abuse-rate-limit
    # Tests have shown that max deletion rate without running into rate limits is ~650 Tags/min.
    PARALLEL_TASKS = 2
    sem = asyncio.Semaphore(PARALLEL_TASKS)

    needs_retry = False
    conn = aiohttp.TCPConnector(
        limit_per_host=LIMIT_SIMULTANEOUS_CONNECTIONS_TO_SAME_ENDPOINT
    )
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            tasks = [
                asyncio.create_task(delete_tag(context, session, tag, token, sem))
                for tag in tags_to_delete
            ]

            status_counter_map: dict[int, int] = {}
            needs_retry = False

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
                    needs_retry = True
                    for t in tasks:
                        if not t.done():
                            t.cancel()
                    break

        finally:
            # ensure all tasks are concluded to suppress warnings
            await asyncio.gather(*tasks, return_exceptions=True)

        print(
            cleandoc(
                f"""
                Deletion run completed.
                Status counters:
                {status_counter_map}
                Retry: {needs_retry}"""
            ),
        )
    return needs_retry


async def _fetch_and_delete_old_tags(context: Context) -> None:
    """
    Cleans all tags in a Docker repository which are older than `min_age_in_days` days.
    1. Gets the auth token from Docker Hub.
    2. Fetches tags from Docker Hub (max. 10.000)
    3. Deletes the tags in a loop until all tags are deleted, or only errors != 429 were raised.
    """

    # 1) Authenticate
    async with aiohttp.ClientSession() as session:

        token = await get_jwt_token(
            session, context.docker_username, context.docker_password
        )
        print("Authenticated successfully.")

    # 1) Fetch old tags
    old_tags = await get_old_tags(context, token)
    if not old_tags:
        print(
            f"Did not find any tag in repo {context.docker_repository} older than {context.min_age_in_days} days."
        )
        return

    # 2) Delete old tags. Repeat until we don't run into a rate limit
    while True:
        tags_to_delete = [tag for tag in old_tags if not tag.deleted]
        retry = await delete_tags(context, token, tags_to_delete)
        if retry:
            console = Console()
            log_msg = "Waiting 1 minute for rate limit cooldown...({seconds}s)"
            with console.status(
                log_msg.format(seconds=0), spinner="bouncingBall"
            ) as status:
                for i in range(60):
                    time.sleep(1)
                    status.update(log_msg.format(seconds=i), spinner="bouncingBall")
        else:
            break


def fetch_and_delete_old_tags(
    docker_repository: str,
    docker_username: str,
    docker_password: str,
    min_age_in_days: int,
    max_number_tags: int,
):
    asyncio.run(
        _fetch_and_delete_old_tags(
            Context(
                docker_repository,
                docker_username,
                docker_password,
                min_age_in_days,
                max_number_tags,
            )
        )
    )

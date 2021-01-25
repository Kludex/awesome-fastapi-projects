import calendar
import os
import time
from typing import Generator

from github import Github, RateLimitExceededException
from github.Repository import Repository

from fastapi_projects.logger import logger

access_token = os.getenv("ACCESS_TOKEN_GITHUB")
g = Github(access_token)

MAX_FILE_SIZE = 384_000


def find_repositories(interval: int = 60) -> Generator[Repository, None, None]:
    min_value = 0

    while min_value < MAX_FILE_SIZE:
        size = f"{min_value}..{min_value + interval - 1}"
        snippets = g.search_code("fastapi", language="Python", size=size)
        count = 0

        snippets = iter(snippets)
        while True:
            try:
                snippet = next(snippets)
                logger.info(snippet.repository.full_name)
                logger.info(snippet.repository.clone_url)
                yield snippet.repository
                count += 1
            except StopIteration:
                break
            except RateLimitExceededException:
                rate_limit = g.get_rate_limit()
                search_rate_limit = rate_limit.search
                core_rate_limit = rate_limit.core
                if search_rate_limit.remaining == 0:
                    logger.debug(f"search remaining: {search_rate_limit.remaining}")
                    reset_time = calendar.timegm(search_rate_limit.reset.timetuple())
                else:
                    logger.debug(f"core remaining: {core_rate_limit.remaining}")
                    reset_time = calendar.timegm(core_rate_limit.reset.timetuple())
                # add 10 seconds to be sure the rate limit has been reset
                sleep_time = reset_time - calendar.timegm(time.gmtime()) + 10
                time.sleep(sleep_time)
        min_value += interval

        logger.info("Found '%d' snippets.", count)

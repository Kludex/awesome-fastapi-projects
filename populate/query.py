import os
from datetime import datetime, timedelta
from time import sleep

from github import Github
from sqlalchemy.orm.session import Session

from populate.exceptions import ignore_exceptions
from populate.logger import log
from populate.models import Repository

g = Github(os.getenv("GITHUB_TOKEN"))


MAX_SIZE = 50 * (2 ** 10)  # 50 KB
INTERVAL = 2 ** 9  # 512 bytes


@ignore_exceptions
def query_github(session: Session, query: str):
    for from_ in range(0, MAX_SIZE, INTERVAL):
        to = from_ + INTERVAL
        files = g.search_code(query.format(from_=from_, to=to))
        for file in files:
            repo = file.repository
            repo_obj = Repository.get(session, full_name=repo.full_name)
            if repo_obj is not None:
                if repo_obj.updated_at - datetime.now() < timedelta(days=30):
                    continue
                # NOTE: `last_modified`` is not the date of the last commit, but
                # actually the time the repository was last updated.
                if repo.last_modified < repo_obj.updated_at:
                    continue
            repo_obj = Repository(
                full_name=repo.full_name,
                html_url=repo.html_url,
                clone_url=repo.clone_url,
                stargazers=repo.stargazers_count,
            )
            session.add(repo_obj)
            session.commit()
            log.debug(f"Added repository {repo_obj.full_name}.")

            sleep(2)

import os
from time import sleep

from github import ContentFile, Github, PaginatedList

from populate.database import SessionLocal, engine
from populate.models import Base, Repository

# from sqlalchemy import create_engine

QUERY = '"from fastapi import" language:python in:file'  #  size:{from_}..{to}'
MAX_SIZE = 50 * (2 ** 10)  # 50 KB

g = Github(os.getenv("GITHUB_TOKEN"))


# TOKEN = os.getenv("GITHUB_TOKEN")
# token_auth = ApiTokenHeader("Authorization", f"token {TOKEN}")
# git = GitHub("https://api.github.com/", auth=token_auth)


# best_split = git.get_best_split()
# out = []
# for key, value in best_split.items():
#     out.append({"from": key[0], "to": key[1], "count": value})
# with open("best_split.json", "w") as f:
#     json.dump(out, f)


if __name__ == "__main__":
    # TODO: Create migrations setup.
    Base.metadata.create_all(engine)

    # 1. Query projects within a range
    interval = 2 ** 9  # 512 bytes
    with SessionLocal() as session:
        for from_ in range(0, MAX_SIZE, interval):
            to = from_ + interval
            files = g.search_code(QUERY.format(from_=from_, to=to))
            for file in files:
                repo = file.repository
                repo_obj = Repository.get(session, full_name=repo.full_name)
                if repo_obj is not None:
                    # TODO: Check when last commit was made.
                    # If it was recent, update dependencies.
                    continue
                repo_obj = Repository(
                    full_name=repo.full_name,
                    html_url=repo.html_url,
                    clone_url=repo.clone_url,
                    stargazers=repo.stargazers_count,
                )
                session.add(repo_obj)
                session.flush()
                # TODO: Check if repository already analyzed.

                print(repo.full_name)

                sleep(1)

    # 2. Clone repositories
    # 3. Find import statements
    # 4. Store project data into the database
    # 5. Push the sqlite file to gcs

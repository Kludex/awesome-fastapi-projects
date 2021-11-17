import tempfile

from populate.database import SessionLocal
from populate.logger import log
from populate.models import Repository
from populate.query import query_github

if __name__ == "__main__":
    log.debug("Start populate script.")

    query = '"from fastapi import" language:python in:file size:{from_}..{to}'

    with SessionLocal() as session:
        log.debug("Start querying projects.")
        query_github(session, query)

        log.debug("Clone repositories.")
        for repository in session.query(Repository).all():
            with tempfile.TemporaryDirectory() as tmpdir:
                log.debug(f"Cloning {repository.full_name}.")
                repo = repository.clone(tmpdir)

                # dependencies = find_dependencies()

    # 3. Find import statements
    # 4. Store project data into the database
    # 5. Push the sqlite file to gcs

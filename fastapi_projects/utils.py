from github.Repository import Repository

from fastapi_projects.database import SessionManager
from fastapi_projects.models import Project


def skip_repository(repository: Repository) -> bool:
    if repository.fork:
        return True
    with SessionManager() as session:
        name = repository.full_name
        project = session.query(Project).filter(Project.name == name).first()
        if project is None or project.pushed_at < repository.pushed_at:
            return False
    return True

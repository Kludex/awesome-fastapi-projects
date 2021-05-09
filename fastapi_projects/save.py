from typing import List

from github.Repository import Repository
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.sqltypes import Integer

from fastapi_projects.database import SessionManager
from fastapi_projects.models import Dependency, Project


def create_project(repository: Repository, packages: List[str]) -> None:
    project_params = {
        "name": repository.full_name,
        "clone_url": repository.clone_url,
        "url": repository.html_url,
        "pushed_at": repository.pushed_at,
    }
    project = Project(**project_params)
    with SessionManager() as session:
        try:
            session.add(project)
            session.commit()
        except IntegrityError:
            session.rollback()
        for package in packages:
            try:
                dependency = Dependency(name=package)
                project.dependencies.append(dependency)
                session.add(project)
                session.commit()
            except IntegrityError:
                session.rollback()
        print([dependency.name for dependency in project.dependencies])

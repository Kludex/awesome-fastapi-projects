from stdlib_list import stdlib_list

from fastapi_projects.clone import clone_repository
from fastapi_projects.database import Base, engine
from fastapi_projects.files import get_python_files
from fastapi_projects.find import find_repositories
from fastapi_projects.packages import get_packages
from fastapi_projects.save import create_project
from fastapi_projects.utils import skip_repository

ignore = ["fastapi", "uvicorn", "src"]
libraries = stdlib_list("3.8") + ignore

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    for repository in find_repositories():
        packages = set()
        if skip_repository(repository):
            continue
        dir = clone_repository(repository)
        for file in get_python_files(dir):
            packages_per_file = list(get_packages(file))
            packages.update(packages_per_file)
            file.close()
        packages = packages - set(libraries)
        create_project(repository, packages)
        dir.cleanup()

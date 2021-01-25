from fastapi_projects.clone import clone_repository
from fastapi_projects.files import get_python_files
from fastapi_projects.find import find_repositories
from fastapi_projects.packages import get_packages

if __name__ == "__main__":
    for repository in find_repositories():
        dir = clone_repository(repository)
        for file in get_python_files(dir):
            for package in get_packages(file):
                print(package)
            file.close()
        dir.cleanup()

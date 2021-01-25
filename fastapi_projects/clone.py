from tempfile import TemporaryDirectory

from git.repo.base import Repo
from github.Repository import Repository


def clone_repository(repository: Repository) -> TemporaryDirectory:
    dir = TemporaryDirectory()
    Repo.clone_from(repository.clone_url, dir.name)
    return dir

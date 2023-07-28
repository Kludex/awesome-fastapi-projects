"""Module contains the models for the application."""
from typing import NewType

from pydantic import AnyUrl, BaseModel

RepoId = NewType("RepoId", int)
DependencyId = NewType("DependencyId", int)


class RepoCreateData(BaseModel):
    """A repository that is being tracked."""

    url: AnyUrl


class DependencyCreateData(BaseModel):
    """A dependency of a repository."""

    name: str

"""Module contains the models for the application."""
from typing import NewType

from pydantic import AnyUrl, BaseModel, Field

RepoId = NewType("RepoId", int)
DependencyId = NewType("DependencyId", int)


class DependencyCreateData(BaseModel):
    """A dependency of a repository."""

    name: str


class RepoCreateData(BaseModel):
    """A repository that is being tracked."""

    url: AnyUrl
    dependencies: list[DependencyCreateData] = Field(default_factory=list)

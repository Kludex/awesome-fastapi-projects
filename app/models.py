"""Module contains the models for the application."""
from typing import NewType

from pydantic import BaseModel, ConfigDict, NonNegativeInt

# TODO: Organize the types

RepoId = NewType("RepoId", int)
DependencyId = NewType("DependencyId", int)
RevisionHash = NewType("RevisionHash", str)


class DependencyCreateData(BaseModel):
    """A dependency of a repository."""

    name: str


class DependencyDetail(BaseModel):
    """A dependency of a repository."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: DependencyId
    name: str


class RepoDetail(BaseModel):
    """A repository that is being tracked."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: RepoId
    url: str
    description: str
    stars: NonNegativeInt
    source_graph_repo_id: int
    dependencies: list[DependencyDetail]
    last_checked_revision: RevisionHash | None

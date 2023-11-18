"""Module contains the models for the application."""

from pydantic import BaseModel, ConfigDict, NonNegativeInt

from app.types import DependencyId, RepoId, RevisionHash, SourceGraphRepoId


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
    source_graph_repo_id: SourceGraphRepoId | None
    dependencies: list[DependencyDetail]
    last_checked_revision: RevisionHash | None

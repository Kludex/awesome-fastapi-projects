"""The models for the Source Graph data."""
import datetime
from typing import Literal, Self

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    NonNegativeInt,
    TypeAdapter,
    computed_field,
)

from app.types import SourceGraphRepoId


class SourceGraphRepoData(BaseModel):
    """The data of a repository."""

    type: Literal["repo"]
    repo_id: SourceGraphRepoId = Field(..., alias="repositoryID")
    repo_handle: str = Field(..., alias="repository")
    stars: NonNegativeInt = Field(..., alias="repoStars")
    last_fetched_at: datetime.datetime = Field(..., alias="repoLastFetched")
    description: str = Field(default="")

    @computed_field  # type: ignore[misc]
    @property
    def repo_url(self: Self) -> HttpUrl:
        """The URL of the repository."""
        return TypeAdapter(HttpUrl).validate_python(f"https://{self.repo_handle}")


#: The type adapter for the SourceGraphRepoData.
SourceGraphRepoDataAdapter = TypeAdapter(SourceGraphRepoData)

#: The type adapter for the SourceGraphRepoData list.
SourceGraphRepoDataListAdapter = TypeAdapter(list[SourceGraphRepoData])

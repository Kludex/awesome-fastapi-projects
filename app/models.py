"""Module contains the models for the application."""
from typing import NewType

from pydantic import BaseModel

RepoId = NewType("RepoId", int)
DependencyId = NewType("DependencyId", int)


class DependencyCreateData(BaseModel):
    """A dependency of a repository."""

    name: str

"""Type definitions for the application."""
from typing import NewType

RepoId = NewType("RepoId", int)
DependencyId = NewType("DependencyId", int)
RevisionHash = NewType("RevisionHash", str)
DatabaseRepoId = NewType("DatabaseRepoId", int)

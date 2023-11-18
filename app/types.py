"""Type definitions for the application."""
from typing import NewType

#: The ID of a repository from the database.
RepoId = NewType("RepoId", int)
#: The ID of a repository from the SourceGraph API.
SourceGraphRepoId = NewType("SourceGraphRepoId", int)
#: The ID of a dependency from the database.
DependencyId = NewType("DependencyId", int)
#: The revision hash of a repository.
RevisionHash = NewType("RevisionHash", str)

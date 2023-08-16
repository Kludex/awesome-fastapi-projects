"""Dependencies parsing."""
import asyncio
import subprocess
from collections.abc import Sequence
from typing import NewType

import aiofiles.tempfile
import stamina

from app.database import Repo
from app.models import DependencyCreateData


async def run_command(*cmd: str, cwd: str | None = None) -> str:
    """
    Run the given command in a subprocess and return the stdout as plain text.

    :param cmd: The command to run.
    :param cwd: The working directory to run the command in.
    :return: The stdout result
    """
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(
            f"Command '{cmd}' failed with exit code '{process.returncode}':\n"
            f"[stdout]: '{stdout.decode()}'\n"
            f"[stderr]: '{stderr.decode()}'"
        )

    return stdout.decode()


RevisionHash = NewType("RevisionHash", str)


async def acquire_dependencies_data_for_repository(
    repo: Repo,
) -> tuple[RevisionHash, list[DependencyCreateData]]:
    """
    Acquire dependencies for the given repository.

    The function will use the "third-party-imports" tool to
    parse the third-party dependencies of the repository.

    Since this tool has been written in Rust and is basically
    a CLI tool, the parsing will happen is a subprocess.

    :param repo: A repository for which to return the dependencies.
    :return: The dependencies data required to create the dependencies in the DB.
    """
    async with aiofiles.tempfile.TemporaryDirectory() as directory:
        # Clone the repository
        await run_command(
            "git",
            "clone",
            "--depth",
            "1",
            repo.url,
            directory,
        )

        # Get the latest commit hash
        revision: str = await run_command(
            "git",
            "rev-parse",
            "HEAD",
            cwd=directory,
        )

        if repo.last_checked_revision == revision:
            # Assume there are no new dependencies to return
            # since all the repo dependencies have already
            # been parsed.
            return RevisionHash(revision), []

        # Parse the dependencies
        async for attempt in stamina.retry_context(on=RuntimeError, attempts=3):
            with attempt:
                dependencies: str = await run_command(
                    "third-party-imports",
                    directory,
                )
        if dependencies:
            # Split the dependencies by new line
            dependencies_list: Sequence[str] = dependencies.split("\n")
            # Drop the first two lines (the info lines)
            dependencies_list = (
                dependencies_list[2:] if len(dependencies_list) > 2 else []
            )
        return (
            RevisionHash(revision),
            [
                DependencyCreateData(
                    name=dependency.strip(),
                )
                for dependency in dependencies_list
                if dependency.strip()
            ],
        )

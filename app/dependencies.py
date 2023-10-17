"""Dependencies parsing."""
import asyncio
import subprocess
from collections.abc import Sequence

import aiofiles.tempfile
import stamina
from loguru import logger

from app.database import Repo
from app.models import DependencyCreateData
from app.types import RevisionHash


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
    logger.info(
        "Acquiring the dependencies data for the repo with id {repo_id}.",
        repo_id=repo.id,
        enqueue=True,
    )
    async with aiofiles.tempfile.TemporaryDirectory() as directory:
        # Clone the repository
        logger.info(
            "Cloning the repo with id {repo_id} into the directory {directory}.",
            repo_id=repo.id,
            directory=directory,
            enqueue=True,
        )
        await run_command(
            "git",
            "clone",
            "--depth",
            "1",
            repo.url,
            directory,
        )

        # Get the latest commit hash
        logger.info(
            "Getting the latest commit hash for the repo with id {repo_id}.",
            repo_id=repo.id,
            enqueue=True,
        )
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
            logger.info(
                "The repo with id {repo_id} has already been updated.",
                repo_id=repo.id,
                enqueue=True,
            )
            return RevisionHash(revision), []

        # Parse the dependencies
        async for attempt in stamina.retry_context(on=RuntimeError, attempts=3):
            with attempt:
                logger.info(
                    "Parsing the dependencies for the repo with id {repo_id}.",
                    repo_id=repo.id,
                    enqueue=True,
                )
                dependencies: str = await run_command(
                    "third-party-imports",
                    directory,
                )
        if dependencies:
            logger.info(
                "Successfully parsed the dependencies for the repo with id {repo_id}.",
                repo_id=repo.id,
                enqueue=True,
            )
            # Split the dependencies by new line
            dependencies_list: Sequence[str] = dependencies.split("\n")
            # Drop the first two lines (the info lines)
            dependencies_list = (
                dependencies_list[2:] if len(dependencies_list) > 2 else []
            )
            logger.info(
                "Found {count} dependencies for the repo with id {repo_id}.",
                count=len(dependencies_list),
                repo_id=repo.id,
                enqueue=True,
            )
        else:
            logger.info(
                "No dependencies found for the repo with id {repo_id}.",
                repo_id=repo.id,
                enqueue=True,
            )
            dependencies_list = []
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

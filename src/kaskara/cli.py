"""Provides a simple command-line interface for Kaskara."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from loguru import logger

from kaskara.clang.analyser import ClangAnalyser
from kaskara.clang.post_install import post_install as install_clang_backend
from kaskara.project import Project
from kaskara.spoon.analyser import SpoonAnalyser
from kaskara.spoon.post_install import post_install as install_spoon_backend


def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{level}:</level> {message}",
        level="DEBUG",
        colorize=True,
    )


@click.group()
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="enables verbose logging.",
)
def cli(verbose: bool) -> None:
    if verbose:
        setup_logging()


@cli.group()
def spoon() -> None:
    pass


@spoon.command(
    "install",
    help="Installs the Spoon analyser backend.",
)
@click.option(
    "-f", "--force",
    is_flag=True,
    help="forces reinstallation of the backend.",
)
def spoon_install(force: bool) -> None:
    """Installs the Spoon analyser backend."""
    install_spoon_backend(force=force)


@spoon.command(
    "index",
    help="Indexes a Java project using Spoon.",
)
@click.argument(
    "image",
    type=str,
)
@click.argument(
    "directory",
    type=str,
)
@click.argument(
    "files",
    nargs=-1,
)
@click.option(
    "--save-to",
    type=click.Path(file_okay=True, dir_okay=False, writable=True, resolve_path=True, path_type=Path),
    default=None,
)
@click.option(
    "--mount-binaries/--no-mount-binaries",
    default=True,
    help="mounts the project binaries into the Docker container.",
)
def spoon_index(
    image: str,
    directory: str,
    files: list[str],
    *,
    save_to: Path | None = None,
    mount_binaries: bool = True,
) -> None:
    """Indexes a Java project using Spoon."""
    with (
        Project.load(
            image=image,
            directory=directory,
            files=files,
        ) as project,
        SpoonAnalyser.for_project(
            project=project,
            mount_binaries=mount_binaries,
        ) as analyser,
    ):
        analysis = analyser.run()

        if save_to:
            with save_to.open("w") as file:
                json.dump(analysis.to_dict(), file, indent=2)




@cli.group()
def clang() -> None:
    pass


@clang.command(
    "install",
    help="Installs the Clang analyser backend.",
)
@click.option(
    "-f", "--force",
    is_flag=True,
    help="forces reinstallation of the backend.",
)
def clang_install(force: bool) -> None:
    """Installs the Clang analyser backend."""
    install_clang_backend(force=force)


@clang.command(
    "index",
    help="Indexes a C/C++ project using Clang.",
)
@click.argument(
    "image",
    type=str,
)
@click.argument(
    "directory",
    type=str,
)
@click.argument(
    "files",
    nargs=-1,
)
@click.option(
    "--save-to",
    type=click.Path(file_okay=True, dir_okay=False, writable=True, resolve_path=True, path_type=Path),
    default=None,
)
def clang_index(
    image: str,
    directory: str,
    files: list[str],
    *,
    save_to: Path | None = None,
) -> None:
    """Indexes a C/C++ project using Clang."""
    with (
        Project.load(
            image=image,
            directory=directory,
            files=files,
        ) as project,
        ClangAnalyser.for_project(project) as analyser,
    ):
        analysis = analyser.run()

        if save_to:
            with save_to.open("w") as file:
                json.dump(analysis.to_dict(), file, indent=2)

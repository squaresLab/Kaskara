"""Provides a simple command-line interface for Kaskara."""
from __future__ import annotations

import sys

import click
from loguru import logger

from kaskara.clang.analyser import ClangAnalyser
from kaskara.clang.post_install import post_install as install_clang_backend
from kaskara.project import Project


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
    print("HELLO")


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
def clang_index(
    image: str,
    directory: str,
    files: list[str],
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
        print(analysis)

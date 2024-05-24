__all__ = ("collect_loops",)

import ast

import asttokens
from loguru import logger

from ..container import ProjectContainer
from ..core import FileLocationRange
from ..loops import ProgramLoops
from .util import ast_location, ast_with_tokens


def collect_loops(container: ProjectContainer) -> ProgramLoops:
    """Finds all loops within a Python project given a container."""
    logger.debug(f"collecting loops for project [{container.project}]")
    visitor = CollectLoopsVisitor(container)
    for filename in container.project.files:
        visitor.collect(filename)
    return ProgramLoops.from_body_location_ranges(visitor.locations)


class CollectLoopsVisitor(ast.NodeVisitor):
    def __init__(self, container: ProjectContainer) -> None:
        super().__init__()
        self.atok: asttokens.ASTTokens
        self.container = container
        self.locations: list[FileLocationRange] = []

    def visit_loop(self,
                   node: ast.For | ast.AsyncFor | ast.While,
                   ) -> None:
        self.locations.append(ast_location(self.atok, node.body))
        if node.orelse:
            self.locations.append(ast_location(self.atok, node.orelse))

    visit_For = visit_loop
    visit_AsyncFor = visit_loop
    visit_While = visit_loop

    def collect(self, filename: str) -> None:
        self.atok = ast_with_tokens(self.container, filename)
        project = self.container
        logger.debug(f"collecting loops in file {filename} "
                     f"for project [{project}]")
        self.visit(self.atok.tree)

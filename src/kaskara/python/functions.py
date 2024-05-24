__all__ = ("collect_functions",)

import ast

import asttokens
from loguru import logger

from ..container import ProjectContainer
from ..functions import ProgramFunctions
from .analysis import PythonFunction
from .util import ast_location, ast_with_tokens


def collect_functions(container: ProjectContainer) -> ProgramFunctions:
    """Finds all functions within a Python project given a container."""
    logger.debug(f"collecting functions for project [{container.project}]")
    visitor = CollectFunctionsVisitor(container)
    for filename in container.project.files:
        visitor.collect(filename)
    return ProgramFunctions(visitor.functions)


class CollectFunctionsVisitor(ast.NodeVisitor):
    def __init__(self, container: ProjectContainer) -> None:
        super().__init__()
        self.atok: asttokens.ASTTokens
        self.container = container
        self.functions: list[PythonFunction] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        location = ast_location(self.atok, node)
        body_location = ast_location(self.atok, node.body)
        function = PythonFunction(name=node.name,
                                  location=location,
                                  body_location=body_location)
        logger.debug(f"found function definition: {function}")
        self.functions.append(function)

    def collect(self, filename: str) -> None:
        self.atok = ast_with_tokens(self.container, filename)
        project = self.container
        logger.debug(f"collecting functions in file {filename} "
                     f"for project [{project}]")
        self.visit(self.atok.tree)

# -*- coding: utf-8 -*-
__all__ = ('collect_functions',)

from typing import Iterator, Collection, List
import ast

from loguru import logger
import asttokens
import astor

from .analysis import PythonFunction
from .util import ast_with_tokens, ast_location
from ..container import ProjectContainer
from ..core import Location, FileLocationRange, LocationRange
from ..functions import ProgramFunctions


def collect_functions(container: ProjectContainer) -> ProgramFunctions:
    """Finds all functions within a Python project given a container."""
    logger.debug(f'collecting functions for project [{container.project}]')
    visitor = CollectFunctionsVisitor(container)
    for filename in container.project.files:
        visitor.collect(filename)
    return ProgramFunctions(visitor.functions)


class CollectFunctionsVisitor(ast.NodeVisitor):
    def __init__(self, container: ProjectContainer) -> None:
        super().__init__()
        self.atok: asttokens.ASTTokens
        self.container = container
        self.functions: List[PythonFunction] = []

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
        logger.debug(f'collecting functions in file {filename} '
                     f'for project [{project}]')
        self.visit(self.atok.tree)

from __future__ import annotations

__all__ = ("collect_statements",)

import ast
import typing as t

import astor
from loguru import logger

from kaskara.python.analysis import PythonStatement
from kaskara.python.util import ast_location, ast_with_tokens
from kaskara.statements import ProgramStatements

if t.TYPE_CHECKING:
    import asttokens

    from kaskara.container import ProjectContainer

STMT_CLASS_NAMES = {
    "FunctionDef",
    "AsyncFunctionDef",
    "ClassDef",
    "Return",
    "Delete",
    "Assign",
    "AugAssign",
    "AnnAssign",
    "For",
    "AsyncFor",
    "While",
    "If",
    "With",
    "AsyncWith",
    "Raise",
    "Try",
    "Assert",
    "Import",
    "ImportFrom",
    "Global",
    "Nonlocal",
    "Expr",
    "Pass",
    "Break",
    "Continue",
}


def collect_statements(container: ProjectContainer) -> ProgramStatements:
    """Finds all statements within a Python project given a container."""
    logger.debug(f"collecting statements for project [{container.project}]")
    visitor = CollectStatementsVisitor(container)
    for filename in container.project.files:
        visitor.collect(filename)
    return ProgramStatements(
        container.project.directory,
        visitor.statements,
    )


class CollectStatementsVisitor(ast.NodeVisitor):
    def __init__(self, container: ProjectContainer) -> None:
        super().__init__()
        self.atok: asttokens.ASTTokens
        self.container = container
        self.statements: list[PythonStatement] = []

    def visit_Module(self, node: ast.Module) -> None:
        for stmt in node.body:
            self.visit(stmt)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        for stmt in node.body:
            self.visit(stmt)

    def generic_visit(self, node: ast.AST) -> None:
        logger.debug(f"visiting node: {node}")
        if node.__class__.__name__ not in STMT_CLASS_NAMES:
            return
        self._collect_stmt(node)
        super().generic_visit(node)

    def _collect_stmt(self, node: ast.AST) -> None:
        kind = node.__class__.__name__
        canonical = astor.to_source(node)
        location = ast_location(self.atok, node)
        source = self.atok.get_text(node)
        stmt = PythonStatement(
            kind=kind,
            content=source,
            canonical=canonical,
            location=location,
        )
        logger.debug(f"found statement: {stmt}")
        logger.debug(f"statement at location: {location}")
        self.statements.append(stmt)

    def collect(self, filename: str) -> None:
        self.atok = ast_with_tokens(self.container, filename)
        project = self.container
        logger.debug(f"collecting statements in file {filename} "
                     f"for project [{project}]")
        self.visit(self.atok.tree)  # type: ignore

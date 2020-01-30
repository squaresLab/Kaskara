# -*- coding: utf-8 -*-
__all__ = ('Statement', 'ProgramStatements')

from typing import FrozenSet, Dict, List, Iterable, Iterator, Optional
import abc

from loguru import logger

from .core import FileLocationRange, FileLocation, FileLine
from .insertions import ProgramInsertionPoints, InsertionPoint


class Statement(abc.ABC):
    """Provides a description of a program statement.

    Attributes
    ----------
    kind: str
        The name of the kind of statement.
    content: str
        The original source code for this statement.
    canonical: str
        The canonical form of the source code for this statement.
    location: FileLocationRange
        The range of locations spanned by this statement.
    visible: FrozenSet[str], optional
        The set of visible symbols at this statement, if known.
    """
    @property
    @abc.abstractmethod
    def kind(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def content(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def canonical(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def visible(self) -> Optional[FrozenSet[str]]:
        ...

    @property
    @abc.abstractmethod
    def location(self) -> FileLocationRange:
        ...


class ProgramStatements:
    def __init__(self, statements: Iterable[Statement]) -> None:
        self.__statements = list(statements)
        logger.debug("indexing statements by file")
        self.__file_to_statements: Dict[str, List[Statement]] = {}
        for statement in statements:
            filename = statement.location.filename
            if filename not in self.__file_to_statements:
                self.__file_to_statements[filename] = []
            self.__file_to_statements[filename].append(statement)
        summary = '\n'.join(f"  {fn}: {len(stmts)} statements" for (fn, stmts)
                            in self.__file_to_statements.items())
        logger.debug(f'indexed statements by file:\n{summary}')

    def __iter__(self) -> Iterator[Statement]:
        yield from self.__statements

    def in_file(self, fn: str) -> Iterator[Statement]:
        """Returns an iterator over the statements belonging to a file."""
        yield from self.__file_to_statements.get(fn, [])

    def at_line(self, line: FileLine) -> Iterator[Statement]:
        """Returns an iterator over the statements located at a given line."""
        num = line.num
        for stmt in self.in_file(line.filename):
            if stmt.location.start.line == num:
                yield stmt

    def insertions(self) -> ProgramInsertionPoints:
        logger.debug('computing insertion points')
        points: List[InsertionPoint] = []
        for stmt in self:
            location = FileLocation(stmt.location.filename,
                                    stmt.location.stop)
            point = InsertionPoint(location, stmt.visible)

            # FIXME do not insert after a return

            points.append(point)
        db = ProgramInsertionPoints(points)
        logger.debug('computed insertion points')
        return db

# -*- coding: utf-8 -*-
__all__ = ('Statement', 'ProgramStatements')

from typing import FrozenSet, Dict, Any, List, Iterator, Mapping, Sequence
import json
import logging

import attr

from .core import FileLocationRange, FileLocation, FileLine
from .insertions import InsertionPointDB, InsertionPoint
from .project import Project
from .util import abs_to_rel_flocrange, rel_to_abs_flocrange

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@attr.s(frozen=True, slots=True, auto_attribs=True)
class Statement:
    content: str
    canonical: str
    kind: str  # FIXME this is super memory inefficient
    location: FileLocationRange
    reads: FrozenSet[str]
    writes: FrozenSet[str]
    visible: FrozenSet[str]
    declares: FrozenSet[str]
    live_before: FrozenSet[str]
    requires_syntax: FrozenSet[str]

    @staticmethod
    def from_dict(project: Project, d: Mapping[str, Any]) -> 'Statement':
        # FIXME
        location = FileLocationRange.from_string(d['location'])
        location = abs_to_rel_flocrange(project.directory, location)
        return Statement(d['content'],
                         d['canonical'],
                         d['kind'],
                         location,
                         frozenset(d.get('reads', [])),
                         frozenset(d.get('writes', [])),
                         frozenset(d.get('visible', [])),
                         frozenset(d.get('decls', [])),
                         frozenset(d.get('live_before', [])),
                         frozenset(d.get('requires_syntax', [])))


class ProgramStatements:
    @classmethod
    def from_file(cls, project: Project, filename: str) -> 'ProgramStatements':
        logger.debug('reading statement database from file: %s', filename)
        with open(filename, 'r') as fh:
            dict_ = json.load(fh)
        statements = ProgramStatements.from_dict(project, dict_)
        logger.debug("read statement database from file: %s", filename)
        return statements

    @staticmethod
    def from_dict(project: Project,
                  d: Sequence[Mapping[str, Any]]
                  ) -> 'ProgramStatements':
        statements = [Statement.from_dict(project, dd) for dd in d]
        return ProgramStatements(statements)

    def __init__(self, statements: List[Statement]) -> None:
        self.__statements = statements
        logger.debug("indexing statements by file")
        self.__file_to_statements = {}  # type: Dict[str, List[Statement]]
        for statement in statements:
            filename = statement.location.filename
            if filename not in self.__file_to_statements:
                self.__file_to_statements[filename] = []
            self.__file_to_statements[filename].append(statement)
        summary = ["  {}: {} statements".format(fn, len(stmts))
                   for (fn, stmts) in self.__file_to_statements.items()]
        logger.debug("indexed statements by file:\n%s", '\n'.join(summary))

    def __iter__(self) -> Iterator[Statement]:
        yield from self.__statements

    def in_file(self, fn: str) -> Iterator[Statement]:
        """
        Returns an iterator over all of the statements belonging to a file.
        """
        yield from self.__file_to_statements.get(fn, [])

    def at_line(self, line: FileLine) -> Iterator[Statement]:
        """
        Returns an iterator over all of the statements located at a given line.
        """
        num = line.num
        for stmt in self.in_file(line.filename):
            if stmt.location.start.line == num:
                yield stmt

    def insertions(self) -> InsertionPointDB:
        logger.debug("computing insertion points")
        points: List[InsertionPoint] = []
        for stmt in self:
            location = FileLocation(stmt.location.filename,
                                    stmt.location.stop)
            point = InsertionPoint(location, stmt.visible)

            # FIXME do not insert after a return

            points.append(point)
        db = InsertionPointDB(points)
        logger.debug("computed insertion points")
        return db

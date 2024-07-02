from __future__ import annotations

__all__ = ("Statement", "ProgramStatements")

import abc
import os
import typing as t
from dataclasses import dataclass, field

from loguru import logger

from .core import FileLine, FileLocation, FileLocationRange
from .insertions import InsertionPoint, ProgramInsertionPoints

if t.TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from kaskara.project import Project

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
    def visible(self) -> frozenset[str] | None:
        ...

    @property
    @abc.abstractmethod
    def location(self) -> FileLocationRange:
        ...

    @abc.abstractmethod
    def with_relative_locations(self, base: str) -> t.Self:
        """Creates a new instance with relative file locations."""
        raise NotImplementedError

    @abc.abstractmethod
    def to_dict(self) -> dict[str, t.Any]:
        """Returns a JSON-serializable dictionary representation of the statement."""
        raise NotImplementedError


@dataclass
class ProgramStatements:
    _project: Project
    _statements: t.Sequence[Statement]
    _file_to_statements: t.Mapping[
        str,
        t.Sequence[Statement],
    ] = field(init=False)

    def __post_init__(self) -> None:
        file_to_statements: t.MutableMapping[
            str,
            t.MutableSequence[Statement],
        ] = {}

        for statement in self._statements:
            filename = statement.location.filename
            if filename not in file_to_statements:
                file_to_statements[filename] = []
            file_to_statements[filename].append(statement)

        self._file_to_statements = file_to_statements

        summary = "\n".join(
            f"  {fn}: {len(stmts)} statements" for (fn, stmts)
            in self._file_to_statements.items()
        )
        logger.debug(f"indexed statements by file:\n{summary}")

    def with_relative_locations(self, base: str) -> ProgramStatements:
        """Creates a new instance with relative file locations."""
        return self.build(
            project=self._project,
            statements=(stmt.with_relative_locations(base) for stmt in self),
        )

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "statements": [stmt.to_dict() for stmt in self],
        }

    @classmethod
    def build(
        cls,
        project: Project,
        statements: Iterable[Statement],
    ) -> ProgramStatements:
        return cls(project, list(statements))

    def __len__(self) -> int:
        """Returns the number of statements in this collection."""
        return len(self._statements)

    def __iter__(self) -> Iterator[Statement]:
        yield from self._statements

    def in_file(self, filename: str) -> Iterator[Statement]:
        """Returns an iterator over the statements belonging to a file."""
        if os.path.isabs(filename):
            start = self._project.directory
            filename = os.path.relpath(filename, start=start)

        yield from self._file_to_statements.get(filename, [])

    def at_line(self, line: FileLine) -> Iterator[Statement]:
        """Returns an iterator over the statements located at a given line."""
        num = line.num
        for stmt in self.in_file(line.filename):
            if stmt.location.start.line == num:
                yield stmt

    def insertions(self) -> ProgramInsertionPoints:
        logger.debug("computing insertion points")
        points: list[InsertionPoint] = []
        for stmt in self:
            location = FileLocation(stmt.location.filename,
                                    stmt.location.stop)
            point = InsertionPoint(location, stmt.visible)

            # FIXME do not insert after a return

            points.append(point)
        db = ProgramInsertionPoints(points)
        logger.debug("computed insertion points")
        return db

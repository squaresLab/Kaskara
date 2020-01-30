# -*- coding: utf-8 -*-
__all__ = ('InsertionPoint', 'ProgramInsertionPoints')

from typing import FrozenSet, Iterable, Iterator, Dict, List, Any, Optional
import attr

from loguru import logger

from .core import FileLocation, FileLine
from .exceptions import KaskaraException
from .util import abs_to_rel_floc, rel_to_abs_floc


@attr.s(frozen=True, slots=True, auto_attribs=True)
class InsertionPoint:
    location: FileLocation
    visible: Optional[FrozenSet[str]] = attr.ib(eq=False, hash=False)


class ProgramInsertionPoints(Iterable[InsertionPoint]):
    def __init__(self, contents: List[InsertionPoint]) -> None:
        self.__contents = contents

        # index by file
        self.__file_insertions: Dict[str, List[InsertionPoint]] = {}
        for ins in contents:
            filename = ins.location.filename
            if filename not in self.__file_insertions:
                self.__file_insertions[filename] = []
            self.__file_insertions[filename].append(ins)

    def __iter__(self) -> Iterator[InsertionPoint]:
        yield from self.__contents

    def in_file(self, filename: str) -> Iterator[InsertionPoint]:
        """Returns an iterator over all insertion points in a given file."""
        logger.debug("finding insertion points in file: %s", filename)
        yield from self.__file_insertions.get(filename, [])

    def at_line(self, line: FileLine) -> Iterator[InsertionPoint]:
        """
        Returns an iterator over all of the insertion points located at a
        given line.
        """
        logger.debug(f"finding insertion points at line: {line}")
        filename: str = line.filename
        line_num: int = line.num
        for ins in self.in_file(filename):
            if line_num == ins.location.line:
                logger.debug(f"found insertion point at line [{line}]: {ins}")
                yield ins

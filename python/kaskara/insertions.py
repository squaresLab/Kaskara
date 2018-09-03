__all__ = ['InsertionPointDB', 'InsertionPoint']

from typing import FrozenSet, Iterable, Iterator, Dict, List, Any
import logging
import json
import attr
import os

from bugzoo.client import Client as BugZooClient
from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container

from .core import FileLocation, FileLine
from .exceptions import BondException
from .util import abs_to_rel_floc, rel_to_abs_floc

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@attr.s(frozen=True, repr=False)
class InsertionPoint(object):
    location = attr.ib(type=FileLocation)
    visible = attr.ib(type=FrozenSet[str])

    @staticmethod
    def from_dict(d: Dict[str, str],
                  snapshot: Snapshot
                  ) -> 'InsertionPoint':
        location = FileLocation.from_string(d['location'])
        location = abs_to_rel_floc(snapshot.source_dir, location)
        visible = frozenset(d['visible'])
        return InsertionPoint(location, visible)

    def __repr__(self) -> str:
        fmt = "InsertionPoint('{}', [{}])"
        return fmt.format(self.location, ', '.join(self.visible))

    def to_dict(self, snapshot: Snapshot) -> Dict[str, Any]:
        loc = rel_to_abs_floc(snapshot.source_dir, self.location)
        return {'location': str(loc),
                'visible': [sym for sym in self.visible]}


class InsertionPointDB(Iterable[InsertionPoint]):
    def __init__(self, contents: List[InsertionPoint]) -> None:
        self.__contents = contents

        # index by file
        self.__file_insertions = {}  # type: Dict[str, List[InsertionPoint]]
        for ins in contents:
            filename = ins.location.filename
            if filename not in self.__file_insertions:
                self.__file_insertions[filename] = []
            self.__file_insertions[filename].append(ins)

    @staticmethod
    def build(client_bugzoo: BugZooClient,
              snapshot: Snapshot,
              files: List[str],
              container: Container,
              *,
              ignore_exit_code: bool = False
              ) -> 'InsertionPointDB':
        out_fn = "insertion-points.json"
        cmd = "kaskara-insertion-point-finder {}".format(' '.join(files))
        workdir = snapshot.source_dir
        outcome = client_bugzoo.containers.exec(container,
                                                cmd,
                                                context=workdir)

        if not ignore_exit_code and outcome.code != 0:
            msg = "kaskara-insertion-point-finder exited with non-zero code: {}"
            msg = msg.format(outcome.code)
            raise BondException(msg)

        output = client_bugzoo.files.read(container, out_fn)
        jsn = json.loads(output)  # type: List[Dict[str, str]]
        return InsertionPointDB.from_dict(jsn, snapshot)

    @staticmethod
    def from_dict(d: List[Dict[str, Any]],
                  snapshot: Snapshot
                  ) -> 'InsertionPointDB':
        contents = [InsertionPoint.from_dict(dd, snapshot) for dd in d]
        return InsertionPointDB(contents)

    def __iter__(self) -> Iterator[InsertionPoint]:
        yield from self.__contents

    def in_file(self, fn: str) -> Iterator[InsertionPoint]:
        """
        Returns an iterator over all of the insertion points in a given file.
        """
        logger.debug("finding insertion points in file: %s", fn)
        yield from self.__file_insertions.get(fn, [])

    def at_line(self, line: FileLine) -> Iterator[InsertionPoint]:
        """
        Returns an iterator over all of the insertion points located at a
        given line.
        """
        logger.debug("finding insertion points at line: %s", str(line))
        filename = line.filename  # type: str
        line_num = line.num  # type: int
        for ins in self.in_file(filename):
            if line_num == ins.location.line:
                logger.debug("found insertion point at line [%s]: %s",
                             str(line), ins)
                yield ins

    def to_dict(self, snapshot: Snapshot) -> List[Dict[str, Any]]:
        return [i.to_dict(snapshot) for i in self]

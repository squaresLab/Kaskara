# -*- coding: utf-8 -*-
__all__ = ('ProgramLoops',)

from typing import List, Dict, Iterable
import json
import logging

import attr
from bugzoo.util import indent
from bugzoo.client import Client as BugZooClient
from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container

from .core import FileLocation, FileLocationRange, FileLocationRangeSet
from .exceptions import BondException
from .util import abs_to_rel_flocrange

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ProgramLoops:
    """Maintains information about all loops within a program."""
    _covered_by_loop_bodies: FileLocationRangeSet

    @staticmethod
    def from_body_location_ranges(bodies: Iterable[FileLocationRange]
                                  ) -> 'ProgramLoops':
        return ProgramLoops(FileLocationRangeSet(bodies))

    def is_within_loop(self, location: FileLocation) -> bool:
        """Checks whether a given location is enclosed within a loop."""
        return self._covered_by_loop_bodies.contains(location)


def find_loops(client_bugzoo: BugZooClient,
               snapshot: Snapshot,
               files: List[str],
               container: Container,
               *,
               ignore_exit_code: bool = False
               ) -> ProgramLoops:
    loop_bodies: List[FileLocationRange] = []

    out_fn = "loops.json"
    cmd = "kaskara-loop-finder {}".format(' '.join(files))
    workdir = snapshot.source_dir
    logger.debug("executing loop finder [%s]: %s", workdir, cmd)
    outcome = client_bugzoo.containers.exec(container, cmd, context=workdir)
    logger.debug("executed loop finder [%d]:\n%s",
                 outcome.code, indent(outcome.output, 2))

    if not ignore_exit_code and outcome.code != 0:
        msg = "loop finder exited with non-zero code: {}"
        msg = msg.format(outcome.code)
        raise BondException(msg)

    logger.debug("reading loop analysis results from file: %s", out_fn)
    output = client_bugzoo.files.read(container, out_fn)
    jsn = json.loads(output)  # type: List[Dict[str, str]]
    for loop_info in jsn:
        loc = FileLocationRange.from_string(loop_info['body'])
        loc = abs_to_rel_flocrange(snapshot.source_dir, loc)
        loop_bodies.append(loc)
    logger.debug("finished reading loop analysis results")

    return ProgramLoops.from_body_location_ranges(loop_bodies)

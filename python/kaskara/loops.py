from typing import List, Dict
import json
import logging

from bugzoo.util import indent
from bugzoo.client import Client as BugZooClient
from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container

from .core import FileLocationRange
from .exceptions import BondException
from .util import abs_to_rel_flocrange

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


def find_loops(client_bugzoo: BugZooClient,
               snapshot: Snapshot,
               files: List[str],
               container: Container,
               *,
               ignore_exit_code: bool = False
               ) -> List[FileLocationRange]:
    loop_bodies = []  # type: List[FileLocationRange]

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

    return loop_bodies

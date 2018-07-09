from typing import List, Dict
import json

from bugzoo.client import Client as BugZooClient
from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container

from .core import FileLocationRange
from .exceptions import BondException
from .util import abs_to_rel_flocrange


def find_loops(client_bugzoo: BugZooClient,
               snapshot: Snapshot,
               files: List[str],
               container: Container
               ) -> List[FileLocationRange]:
    loop_bodies = []  # type: List[FileLocationRange]

    out_fn = "loops.json"
    cmd = "kaskara-loop-finder {}".format(' '.join(files))
    workdir = "/ros_ws"
    outcome = client_bugzoo.containers.exec(container, cmd, context=workdir)

    if outcome.code != 0:
        msg = "loop finder exited with non-zero code: {}"
        msg = msg.format(outcome.code)
        raise BondException(msg)

    output = client_bugzoo.files.read(container, out_fn)
    jsn = json.loads(output)  # type: List[Dict[str, str]]
    for loop_info in jsn:
        loc = FileLocationRange.from_string(loop_info['body'])
        loc = abs_to_rel_flocrange(snapshot.source_dir, loc)
        loop_bodies.append(loc)

    return loop_bodies

from typing import List, Dict, Tuple
import json

from bugzoo.client import Client as BugZooClient
from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container

from .core import FileLocationRange
from .exceptions import BondException


def find_functions(client_bugzoo: BugZooClient,
                   snapshot: Snapshot,
                   files: List[str],
                   container: Container
                   ) -> Tuple[List[FileLocationRange], List[FileLocationRange]]:
    function_bodies = []  # type: List[FileLocationRange]
    void_function_bodies = []  # type: List[FileLocationRange]

    out_fn = "functions.json"
    cmd = "kaskara-function-scanner {}".format(' '.join(files))
    workdir = "/ros_ws"
    outcome = client_bugzoo.containers.exec(container, cmd, context=workdir)

    if outcome.code != 0:
        msg = "kaskara-function-scanner exited with non-zero code: {}"
        msg = msg.format(outcome.code)
        raise BondException(msg)

    output = client_bugzoo.files.read(container, out_fn)
    jsn = json.loads(output)  # type: List[Dict[str, str]]
    for loop_info in jsn:
        loc = FileLocationRange.from_string(loop_info['body'])
        function_bodies.append(loc)

        if loop_info['return-type'] == 'void':
            void_function_bodies.append(loc)

    return (function_bodies, void_function_bodies)

__all__ = ['InsertionPointDB', 'InsertionPoint']

from typing import FrozenSet, Iterable, Iterator, Dict, List, Any
import json
import attr

from bugzoo.client import Client as BugZooClient
from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container

from .core import FileLocation
from .exceptions import BondException


@attr.s(frozen=True, repr=False)
class InsertionPoint(object):
    location = attr.ib(type=FileLocation)
    visible = attr.ib(type=FrozenSet[str])

    @staticmethod
    def from_dict(d: Dict[str, str]) -> 'InsertionPoint':
        location = FileLocation.from_string(d['location'])
        visible = frozenset(d['visible'])
        return InsertionPoint(location, visible)

    def __repr__(self) -> str:
        fmt = "InsertionPoint('{}', [{}])"
        return fmt.format(self.location, ', '.join(self.visible))

    def to_dict(self) -> Dict[str, Any]:
        return {'location': str(self.location),
                'visible': [sym for sym in self.visible]}


class InsertionPointDB(Iterable[InsertionPoint]):
    def __init__(self, contents: List[InsertionPoint]) -> None:
        self.__contents = contents

    @staticmethod
    def build(client_bugzoo: BugZooClient,
              snapshot: Snapshot,
              files: List[str],
              container: Container
              ) -> 'InsertionPointDB':
        out_fn = "insertion-points.json"
        cmd = "kaskara-insertion-point-finder {}".format(' '.join(files))
        workdir = "/ros_ws"
        outcome = client_bugzoo.containers.exec(container,
                                                cmd,
                                                context=workdir)

        print(outcome.output)

        if outcome.code != 0:
            msg = "kaskara-insertion-point-finder exited with non-zero code: {}"
            msg = msg.format(outcome.code)
            raise BondException(msg)

        output = client_bugzoo.files.read(container, out_fn)
        jsn = json.loads(output)  # type: List[Dict[str, str]]
        return InsertionPointDB.from_dict(jsn)

    @staticmethod
    def from_dict(d: List[Dict[str, Any]]) -> 'InsertionPointDB':
        contents = [InsertionPoint.from_dict(dd) for dd in d]
        return InsertionPointDB(contents)

    def __iter__(self) -> Iterator[InsertionPoint]:
        yield from self.__contents

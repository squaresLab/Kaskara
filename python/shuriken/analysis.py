__all__ = ['Analysis']

from typing import List, Optional

from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container
from bugzoo.client import Client as BugZooClient

from .core import FileLocation, FileLocationRange, FileLocationRangeSet
from .loops import find_loops


class Analysis(object):
    @staticmethod
    def build(client_bugzoo: BugZooClient,
              snapshot: Snapshot,
              files: List[str]
              ) -> 'Analysis':
        # FIXME assumes binaries are already present in container
        container = None  # type: Optional[Container]
        try:
            container = client_bugzoo.containers.provision(snapshot)
            loop_bodies = find_loops(client_bugzoo, snapshot, files, container)
            return Analysis(loop_bodies, [])
        finally:
            if container:
                del client_bugzoo.containers[container.uid]

    def __init__(self,
                 loop_bodies: List[FileLocationRange],
                 function_bodies: List[FileLocationRange]
                 ) -> None:
        self.__location_bodies = FileLocationRangeSet(loop_bodies)
        self.__location_functions = FileLocationRangeSet(function_bodies)

    def is_inside_loop(self, location: FileLocation) -> bool:
        return location in self.__location_bodies

    def is_inside_function(self, location: FileLocation) -> bool:
        return location in self.__location_functions

    def is_inside_void_function(self, location: FileLocation) -> bool:
        raise NotImplementedError

    def dump(self) -> None:
        print(self.__location_bodies)

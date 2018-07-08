__all__ = ['Analysis']

from typing import List, Optional

from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container
from bugzoo.client import Client as BugZooClient

from .core import FileLocation, FileLocationRange, FileLocationRangeSet
from .loops import find_loops
from .functions import FunctionDB
from .insertions import InsertionPointDB


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
            loop_bodies = \
                find_loops(client_bugzoo, snapshot, files, container)
            db_function = \
                FunctionDB.build(client_bugzoo, snapshot, files, container)
            db_insertion = \
                InsertionPointDB.build(client_bugzoo, snapshot, files, container)
            return Analysis(loop_bodies, db_function, db_insertion)
        finally:
            if container:
                del client_bugzoo.containers[container.uid]

    def __init__(self,
                 loop_bodies: List[FileLocationRange],
                 db_function: FunctionDB,
                 db_insertion: InsertionPointDB

                 ) -> None:
        self.__location_bodies = FileLocationRangeSet(loop_bodies)
        self.__db_function = db_function
        self.__db_insertion = db_insertion

    @property
    def functions(self) -> FunctionDB:
        return self.__db_function

    @property
    def insertions(self) -> InsertionPointDB:
        return self.__db_insertion

    def is_inside_loop(self, location: FileLocation) -> bool:
        return location in self.__location_bodies

    def is_inside_function(self, location: FileLocation) -> bool:
        return self.__db_function.encloses(location) is not None

    def is_inside_void_function(self, location: FileLocation) -> bool:
        f = self.__db_function.encloses(location)
        return f is not None and f.return_type == 'void'

    def dump(self) -> None:
        print("LOOPS: {}".format(self.__location_bodies))
        print("INSERTIONS: {}".format([i for i in self.insertions]))

# -*- coding: utf-8 -*-
__all__ = ('Analysis',)

from typing import List, Optional, Dict, Any
import json

from bugzoo.core.tool import Tool as Plugin
from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container
from bugzoo.client import Client as BugZooClient

from .core import FileLocation, FileLocationRange, FileLocationRangeSet
from .loops import find_loops, ProgramLoops
from .functions import FunctionDB
from .insertions import InsertionPointDB
from .statements import ProgramStatements

PLUGIN = Plugin(name='kaskara',
                image='squareslab/kaskara',
                environment={'PATH': '/opt/kaskara/scripts:${PATH}'})


class Analysis:
    @staticmethod
    def build(client_bugzoo: BugZooClient,
              snapshot: Snapshot,
              files: List[str],
              *,
              ignore_exit_code: bool = False
              ) -> 'Analysis':
        # FIXME assumes binaries are already present in container
        container = None  # type: Optional[Container]
        try:
            container = client_bugzoo.containers.provision(snapshot,
                                                           plugins=[PLUGIN])
            program_loops = \
                find_loops(client_bugzoo, snapshot, files, container,
                           ignore_exit_code=ignore_exit_code)
            db_function = \
                FunctionDB.build(client_bugzoo, snapshot, files, container,
                                 ignore_exit_code=ignore_exit_code)
            db_statements = \
                ProgramStatements.build(client_bugzoo,
                                        snapshot,
                                        files,
                                        container,
                                        ignore_exit_code=ignore_exit_code)
            return Analysis(program_loops,
                            db_function,
                            db_statements)
        finally:
            if container:
                del client_bugzoo.containers[container.uid]

    def __init__(self,
                 program_loops: ProgramLoops,
                 db_function: FunctionDB,
                 db_statement: ProgramStatements
                 ) -> None:
        self.__program_loops = program_loops
        self.__db_function = db_function
        self.__db_insertion = db_statement.insertions()
        self.__db_statement = db_statement

    @property
    def functions(self) -> FunctionDB:
        return self.__db_function

    @property
    def statements(self) -> ProgramStatements:
        return self.__db_statement

    @property
    def insertions(self) -> InsertionPointDB:
        return self.__db_insertion

    @property
    def loops(self) -> ProgramLoops:
        return self.__program_loops

    def is_inside_loop(self, location: FileLocation) -> bool:
        return self.__program_loops.is_within_loop(location)

    def is_inside_function(self, location: FileLocation) -> bool:
        return self.__db_function.encloses(location) is not None

    def is_inside_void_function(self, location: FileLocation) -> bool:
        f = self.__db_function.encloses(location)
        return f is not None and f.return_type == 'void'

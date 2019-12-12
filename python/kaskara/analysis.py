# -*- coding: utf-8 -*-
__all__ = ('Analysis',)

from typing import List, Optional, Dict, Any
import json

import attr
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


@attr.s(slots=True, auto_attribs=True, frozen=True)
class Analysis:
    loops: ProgramLoops
    functions: FunctionDB
    statements: ProgramStatements
    insertions: InsertionPointDB

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

            db_insertion = db_statements.insertions()
            return Analysis(loops=program_loops,
                            functions=db_function,
                            statements=db_statements,
                            insertions=db_insertion)
        finally:
            if container:
                del client_bugzoo.containers[container.uid]

    def is_inside_loop(self, location: FileLocation) -> bool:
        return self.loops.is_within_loop(location)

    def is_inside_function(self, location: FileLocation) -> bool:
        return self.functions.encloses(location) is not None

    def is_inside_void_function(self, location: FileLocation) -> bool:
        f = self.functions.encloses(location)
        return f is not None and f.return_type == 'void'

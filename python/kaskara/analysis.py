# -*- coding: utf-8 -*-
__all__ = ('Analysis',)

from typing import List, Optional, Dict, Any
from contextlib import ExitStack
import json

import attr
import docker as _docker
import dockerblade as _dockerblade

from .core import FileLocation, FileLocationRange, FileLocationRangeSet
from .functions import FunctionDB
from .insertions import InsertionPointDB
from .loops import ProgramLoops
from .project import Project
from .statements import ProgramStatements


@attr.s(slots=True, auto_attribs=True, frozen=True)
class Analysis:
    project: Project
    loops: ProgramLoops
    functions: FunctionDB
    statements: ProgramStatements
    insertions: InsertionPointDB

    @staticmethod
    def build(project: Project) -> 'Analysis':
        program_loops = ProgramLoops.build(project)
        db_function = FunctionDB.build(project)
        db_statements = ProgramStatements.build(project)
        db_insertion = db_statements.insertions()
        return Analysis(project=project,
                        loops=program_loops,
                        functions=db_function,
                        statements=db_statements,
                        insertions=db_insertion)

    def is_inside_loop(self, location: FileLocation) -> bool:
        return self.loops.is_within_loop(location)

    def is_inside_function(self, location: FileLocation) -> bool:
        return self.functions.encloses(location) is not None

    def is_inside_void_function(self, location: FileLocation) -> bool:
        f = self.functions.encloses(location)
        return f is not None and f.return_type == 'void'

# -*- coding: utf-8 -*-
__all__ = ('Analysis',)

from typing import List, Optional, Dict, Any
from contextlib import ExitStack
import json

import attr
import docker as _docker
import dockerblade as _dockerblade

from .core import FileLocation, FileLocationRange, FileLocationRangeSet
from .functions import ProgramFunctions
from .insertions import InsertionPointDB
from .loops import ProgramLoops
from .project import Project
from .statements import ProgramStatements


@attr.s(slots=True, auto_attribs=True, frozen=True)
class Analysis:
    """Stores the results of an analysis of a given project.

    Attributes
    ----------
    project: Project
        A description of the project that was analysed.
    loops: ProgramLoops
        The set of loop control-flow statements within the program.
    functions: ProgramFunctions
        The set of functions within the program.
    statements: ProgramStatements
        The set of statements within the program.
    """
    project: Project
    loops: ProgramLoops
    functions: ProgramFunctions
    statements: ProgramStatements
    insertions: InsertionPointDB

    @staticmethod
    def build(project: Project) -> 'Analysis':
        """Performs an analysis of a given project."""
        loops = ProgramLoops.build(project)
        functions = ProgramFunctions.build(project)
        statements = ProgramStatements.build(project)
        insertions = statements.insertions()
        return Analysis(project=project,
                        loops=loops,
                        functions=functions,
                        statements=statements,
                        insertions=insertions)

    def is_inside_loop(self, location: FileLocation) -> bool:
        return self.loops.is_within_loop(location)

    def is_inside_function(self, location: FileLocation) -> bool:
        return self.functions.encloses(location) is not None

    def is_inside_void_function(self, location: FileLocation) -> bool:
        f = self.functions.encloses(location)
        return f is not None and f.return_type == 'void'

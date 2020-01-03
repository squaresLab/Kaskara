# -*- coding: utf-8 -*-
__all__ = ('Analysis',)

import attr

from .core import FileLocation
from .functions import ProgramFunctions
from .insertions import ProgramInsertionPoints
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
    insertions: ProgramInsertionPoints

    def is_inside_loop(self, location: FileLocation) -> bool:
        return self.loops.is_within_loop(location)

    def is_inside_function(self, location: FileLocation) -> bool:
        return self.functions.encloses(location) is not None

    def is_inside_void_function(self, location: FileLocation) -> bool:
        f = self.functions.encloses(location)
        return f is not None and f.return_type == 'void'

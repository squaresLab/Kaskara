from __future__ import annotations

__all__ = ("Analysis",)

import json
import typing as t

import attr

if t.TYPE_CHECKING:
    from kaskara.core import FileLocation
    from kaskara.functions import ProgramFunctions
    from kaskara.insertions import ProgramInsertionPoints
    from kaskara.loops import ProgramLoops
    from kaskara.statements import ProgramStatements


@attr.s(slots=True, auto_attribs=True, frozen=True)
class Analysis:
    """Stores the results of an analysis of a given project.

    Attributes
    ----------
    loops: ProgramLoops
        The set of loop control-flow statements within the program.
    functions: ProgramFunctions
        The set of functions within the program.
    statements: ProgramStatements
        The set of statements within the program.
    """
    loops: ProgramLoops
    functions: ProgramFunctions
    statements: ProgramStatements
    insertions: ProgramInsertionPoints

    def with_relative_locations(self, base: str) -> Analysis:
        return attr.evolve(
            self,
            loops=self.loops.with_relative_locations(base),
            functions=self.functions.with_relative_locations(base),
            statements=self.statements.with_relative_locations(base),
            insertions=self.insertions.with_relative_locations(base),
        )

    def is_inside_loop(self, location: FileLocation) -> bool:
        return self.loops.is_within_loop(location)

    def is_inside_function(self, location: FileLocation) -> bool:
        return self.functions.encloses(location) is not None

    def is_inside_void_function(self, location: FileLocation) -> bool:
        f = self.functions.encloses(location)
        return f is not None and f.return_type == "void"

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "loops": self.loops.to_dict(),
            "functions": self.functions.to_dict(),
            "statements": self.statements.to_dict(),
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

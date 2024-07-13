from __future__ import annotations

__all__ = ("ProgramLoops",)

import os
import typing as t
from dataclasses import dataclass

from .core import (
    FileLocation,
    FileLocationRange,
    FileLocationRangeSet,
    Location,
)

if t.TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class ProgramLoops:
    """Maintains information about all loops within a program."""
    _project_directory: str
    _covered_by_loop_bodies: FileLocationRangeSet

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "covered_by_loop_bodies": [
                str(loc_range) for loc_range in self._covered_by_loop_bodies
            ],
        }

    @classmethod
    def from_body_location_ranges(
        cls,
        project_directory: str,
        bodies: Iterable[FileLocationRange],
    ) -> ProgramLoops:
        return ProgramLoops(
            project_directory,
            FileLocationRangeSet(bodies),
        )

    def merge(self, other: ProgramLoops) -> ProgramLoops:
        covered_by_loop_bodies = self._covered_by_loop_bodies.union(
            other._covered_by_loop_bodies,
        )
        return ProgramLoops(
            _covered_by_loop_bodies=covered_by_loop_bodies,
            _project_directory=self._project_directory,
        )

    def with_relative_locations(self, base: str) -> ProgramLoops:
        """Creates a new instance with relative file locations."""
        covered_by_loop_bodies = self._covered_by_loop_bodies.with_relative_locations(
            base,
        )
        return ProgramLoops(
            _covered_by_loop_bodies=covered_by_loop_bodies,
            _project_directory=self._project_directory,
        )

    def is_within_loop(self, file_location: FileLocation) -> bool:
        """Checks whether a given location is enclosed within a loop."""
        filename = file_location.filename
        if os.path.isabs(filename):
            start = self._project_directory
            filename = os.path.relpath(filename, start=start)
            location = Location(
                line=file_location.line,
                column=file_location.column,
            )
            file_location = FileLocation(
                filename=filename,
                location=location,
            )
        is_within: bool = self._covered_by_loop_bodies.contains(
            file_location,
        )
        return is_within

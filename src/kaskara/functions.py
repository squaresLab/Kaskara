"""Provides functionality for discovering and describing the set of functions contained within a program."""
from __future__ import annotations

__all__ = ("Function", "ProgramFunctions")

import abc
import itertools
import os
import typing as t
from dataclasses import dataclass
from typing import (
    final,
)

if t.TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from kaskara.core import FileLocation, FileLocationRange


class Function(abc.ABC):
    """Provides a concise description of a function definition.

    Attributes
    ----------
    name: str
        The name of the function.
    location: FileLocationRange
        The range of locations spanned by the function.
    body_location: FileLocationRange
        The range of locations spanned by the function body.
    return_type: Optional[str]
        The name of the return type for the function, if known.
    filename: str
        The name of the file to which the function definition belongs.
    """
    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def return_type(self) -> str | None:
        ...

    @property
    @abc.abstractmethod
    def location(self) -> FileLocationRange:
        ...

    @property
    @abc.abstractmethod
    def body_location(self) -> FileLocationRange:
        ...

    @final
    @property
    def filename(self) -> str:
        filename: str = self.location.filename
        return filename

    @abc.abstractmethod
    def with_relative_locations(self, base: str) -> t.Self:
        """Creates a new instance with relative file locations."""
        raise NotImplementedError

    @abc.abstractmethod
    def to_dict(self) -> dict[str, t.Any]:
        """Returns a JSON-serializable dictionary representation of the function."""
        raise NotImplementedError


@dataclass(frozen=True)
class ProgramFunctions(t.Iterable[Function]):
    """Represents the set of functions within an associated program."""
    _project_directory: str
    _filename_to_functions: dict[str, list[Function]]
    _num_functions: int

    @classmethod
    def empty(cls, project_directory: str) -> ProgramFunctions:
        return cls(
            _project_directory=project_directory,
            _filename_to_functions={},
            _num_functions=0,
        )

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "functions": [f.to_dict() for f in self],
        }

    def merge(self, other: ProgramFunctions) -> ProgramFunctions:
        """Merges the results of this analysis and another analysis together."""
        return self.from_functions(
            project_directory=self._project_directory,
            functions=itertools.chain(self, other),
        )

    def with_relative_locations(self, base: str) -> ProgramFunctions:
        """Creates a new instance with relative file locations."""
        functions = [f.with_relative_locations(base) for f in self]
        result = self.from_functions(self._project_directory, functions)
        assert len(result) == len(self)
        return result

    @classmethod
    def from_functions(
        cls,
        project_directory: str,
        functions: Iterable[Function],
    ) -> ProgramFunctions:
        num_functions = 0
        filename_to_functions: dict[str, list[Function]] = {}

        for f in functions:
            if f.filename not in filename_to_functions:
                filename_to_functions[f.filename] = []
            filename_to_functions[f.filename].append(f)
            num_functions += 1

        return cls(
            _project_directory=project_directory,
            _filename_to_functions=filename_to_functions,
            _num_functions=num_functions,
        )

    def encloses(self, location: FileLocation) -> Function | None:
        """Returns the enclosing function, if any, for a given location."""
        for func in self.in_file(location.filename):
            if location in func.location:
                return func
        return None

    def in_file(self, filename: str) -> ProgramFunctions:
        """Returns all of the functions defined in a given file."""
        if os.path.isabs(filename):
            start = self._project_directory
            filename = os.path.relpath(filename, start=start)

        if filename not in self._filename_to_functions:
            return ProgramFunctions.empty(self._project_directory)

        functions = self._filename_to_functions[filename]
        return ProgramFunctions(
            _project_directory=self._project_directory,
            _filename_to_functions={filename: functions},
            _num_functions=len(functions),
        )

    def __len__(self) -> int:
        """Returns a count of the number of functions in the program."""
        return self._num_functions

    def __iter__(self) -> Iterator[Function]:
        """Returns an iterator over the functions in the program."""
        for functions in self._filename_to_functions.values():
            yield from functions

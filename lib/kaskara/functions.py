# -*- coding: utf-8 -*-
"""
This module provides functionality for discovering and describing the set of
functions contained within a program.
"""
__all__ = ('Function', 'ProgramFunctions')

from typing import List, Dict, Tuple, Optional, Iterator, Iterable, Any
from typing_extensions import final
import abc

from .core import FileLocationRange, FileLocation


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
    def return_type(self) -> Optional[str]:
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
        return self.location.filename


class ProgramFunctions:
    """Represents the set of functions within an associated program."""
    def __init__(self, functions: Iterable[Function]) -> None:
        self.__length = 0
        self.__filename_to_functions: Dict[str, List[Function]] = {}
        for f in functions:
            if f.filename not in self.__filename_to_functions:
                self.__filename_to_functions[f.filename] = []
            self.__filename_to_functions[f.filename].append(f)
            self.__length += 1

    def encloses(self, location: FileLocation) -> Optional[Function]:
        """Returns the enclosing function, if any, for a given location."""
        for func in self.in_file(location.filename):
            if location in func.location:
                return func
        return None

    def in_file(self, filename: str) -> Iterator[Function]:
        """Returns an iterator over the functions defined in a given file."""
        yield from self.__filename_to_functions.get(filename, [])

    def __len__(self) -> int:
        """Returns a count of the number of functions in the program."""
        return self.__length

    def __iter__(self) -> Iterator[Function]:
        """Returns an iterator over the functions in the program."""
        for functions in self.__filename_to_functions.values():
            yield from functions

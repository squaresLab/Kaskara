# -*- coding: utf-8 -*-
"""
This module provides functionality for discovering and describing the set of
functions contained within a program.
"""
__all__ = ('FunctionDesc', 'ProgramFunctions')

from typing import List, Dict, Tuple, Optional, Iterator, Iterable, Any
import json
import logging
import os

import attr
import dockerblade as _dockerblade

from .core import FileLocationRange, FileLocation
from .container import ProjectContainer
from .exceptions import KaskaraException
from .project import Project
from .util import abs_to_rel_flocrange, rel_to_abs_flocrange

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@attr.s(frozen=True, slots=True, auto_attribs=True)
class FunctionDesc:
    """Provides a concise description of a function definition."""
    name: str
    location: FileLocationRange
    body: FileLocationRange
    return_type: str
    is_global: bool
    is_pure: bool

    @staticmethod
    def from_dict(project: Project, d: Dict[str, Any]) -> 'FunctionDesc':
        name = d['name']
        location = FileLocationRange.from_string(d['location'])
        location = abs_to_rel_flocrange(project.directory, location)
        body = FileLocationRange.from_string(d['body'])
        body = abs_to_rel_flocrange(project.directory, body)
        return_type = d['return-type']
        is_global = d['global']
        is_pure = d['pure']
        return FunctionDesc(name=name,
                            location=location,
                            body=body,
                            return_type=return_type,
                            is_global=is_global,
                            is_pure=is_pure)

    @property
    def filename(self) -> str:
        return self.location.filename


class ProgramFunctions:
    """Represents the set of functions within an associated program."""
    def __init__(self, functions: Iterable[FunctionDesc]) -> None:
        self.__filename_to_functions: Dict[str, List[FunctionDesc]] = {}
        for f in functions:
            if f.filename not in self.__filename_to_functions:
                self.__filename_to_functions[f.filename] = []
            self.__filename_to_functions[f.filename].append(f)

    def encloses(self,
                 location: FileLocation
                 ) -> Optional[FunctionDesc]:
        """
        Returns the function, if any, that encloses a given location.
        """
        for func in self.in_file(location.filename):
            if location in func.location:
                return func
        return None

    def in_file(self, filename: str) -> Iterator[FunctionDesc]:
        """
        Returns an iterator over all of the functions definitions that are
        contained within a given file.
        """
        yield from self.__filename_to_functions.get(filename, [])

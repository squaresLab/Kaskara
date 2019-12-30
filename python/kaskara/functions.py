# -*- coding: utf-8 -*-
__all__ = ('FunctionDesc', 'FunctionDB')

from typing import List, Dict, Tuple, Optional, Iterator, Iterable, Any
import json
import logging
import os

import attr
import dockerblade as _dockerblade

from .core import FileLocationRange, FileLocation
from .exceptions import BondException
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

    def to_dict(self, project: Project) -> Dict[str, Any]:
        loc = rel_to_abs_flocrange(project.directory, self.location)
        body = rel_to_abs_flocrange(project.directory, self.body)
        return {'name': self.name,
                'location': str(loc),
                'body': str(body),
                'return-type': self.return_type,
                'global': self.is_global,
                'pure': self.is_pure}


class FunctionDB:
    @staticmethod
    def from_dict(project: Project, d: List[Dict[str, Any]]) -> 'FunctionDB':
        return FunctionDB(FunctionDesc.from_dict(project, desc) for desc in d)

    @classmethod
    def build_for_container(cls,
                            project: Project,
                            container: _dockerblade.Container
                            ) -> 'FunctionDB':
        shell = container.shell()
        workdir = project.directory
        output_filename = os.path.join(workdir, 'functions.json')
        command_args = ['/opt/kaskara/scripts/kaskara-function-scanner']
        command_args += project.files
        command = ' '.join(command_args)

        logger.debug('executing function scanner [%s]: %s', workdir, command)
        try:
            shell.check_call(command, cwd=workdir)
        except _dockerblade.CalledProcessError as err:
            msg = f'function scanner failed with code {err.returncode}'
            logger.exception(msg)
            if not project.ignore_errors:
                raise BondException(msg)

        logger.debug('reading results from file: %s', output_filename)
        files = container.filesystem()
        file_contents = files.read(output_filename)
        jsn = json.loads(file_contents)
        funcs = [FunctionDesc.from_dict(project, d) for d in jsn]
        return FunctionDB(funcs)

    @classmethod
    def build(cls, project: Project) -> 'FunctionDB':
        with project.provision() as container:
            return cls.build_for_container(project, container)

    def __init__(self, functions: Iterable[FunctionDesc]) -> None:
        self.__filename_to_functions = \
            {}  # type: Dict[str, List[FunctionDesc]]
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

    def to_dict(self, project: Project) -> List[Dict[str, Any]]:
        d: List[Dict[str, Any]] = []
        for descs in self.__filename_to_functions.values():
            for desc in descs:
                d.append(desc.to_dict(project))
        return d

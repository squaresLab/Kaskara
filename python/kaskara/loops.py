# -*- coding: utf-8 -*-
__all__ = ('ProgramLoops',)

from typing import List, Dict, Iterable
import json
import logging
import os

import attr
import dockerblade as _dockerblade

from .core import FileLocation, FileLocationRange, FileLocationRangeSet
from .exceptions import BondException
from .project import Project
from .util import abs_to_rel_flocrange

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ProgramLoops:
    """Maintains information about all loops within a program."""
    _covered_by_loop_bodies: FileLocationRangeSet

    @classmethod
    def from_body_location_ranges(cls,
                                  bodies: Iterable[FileLocationRange]
                                  ) -> 'ProgramLoops':
        return ProgramLoops(FileLocationRangeSet(bodies))

    def is_within_loop(self, location: FileLocation) -> bool:
        """Checks whether a given location is enclosed within a loop."""
        return self._covered_by_loop_bodies.contains(location)

    @classmethod
    def _from_file_contents(cls,
                            project: Project,
                            contents: str
                            ) -> 'ProgramLoops':
        loop_bodies: List[FileLocationRange] = []
        jsn: List[Dict[str, str]] = json.loads(contents)
        for loop_info in jsn:
            loc = FileLocationRange.from_string(loop_info['body'])
            loc = abs_to_rel_flocrange(project.directory, loc)
            loop_bodies.append(loc)
        logger.debug('finished reading loop analysis results')
        return cls.from_body_location_ranges(loop_bodies)

    @classmethod
    def build_for_container(cls,
                            project: Project,
                            container: _dockerblade.Container
                            ) -> 'ProgramLoops':
        shell = container.shell()
        workdir = project.directory
        command_args = ['/opt/kaskara/scripts/kaskara-loop-finder']
        command_args += project.files
        command = ' '.join(command_args)
        output_filename = os.path.join(workdir, 'loops.json')
        logger.debug('executing loop finder [%s]: %s', workdir, command)
        try:
            shell.check_call(command, cwd=workdir)
        except _dockerblade.CalledProcessError as err:
            msg = f'loop finder failed with code {err.returncode}'
            logger.exception(msg)
            if not project.ignore_errors:
                raise BondException(msg)

        logger.debug('reading results from file: %s', output_filename)
        files = container.filesystem()
        file_contents = files.read(output_filename)
        return cls._from_file_contents(project, file_contents)

    @classmethod
    def build(cls, project: Project) -> 'ProgramLoops':
        with project.provision() as container:
            return cls.build_for_container(project, container)

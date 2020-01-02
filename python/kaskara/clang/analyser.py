# -*- coding: utf-8 -*-
__all__ = ('ClangAnalyser',)

from typing import Any, List, Mapping, Sequence
import json
import logging
import os

import dockerblade as _dockerblade

from ..analyser import Analyser
from ..analysis import Analysis
from ..core import FileLocationRange
from ..container import ProjectContainer
from ..exceptions import KaskaraException
from ..functions import ProgramFunctions, FunctionDesc
from ..loops import ProgramLoops
from ..project import Project
from ..statements import ProgramStatements
from ..util import abs_to_rel_flocrange

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ClangAnalyser(Analyser):
    def analyse(self, project: Project) -> Analysis:
        with project.provision() as container:
            return self._analyse_container(container)

    def _analyse_container(self, container: ProjectContainer) -> Analysis:
        loops = self._find_loops(container)
        functions = self._find_functions(container)
        statements = self._find_statements(container)
        insertions = statements.insertions()
        return Analysis(project=container.project,
                        loops=loops,
                        functions=functions,
                        statements=statements,
                        insertions=insertions)

    def _find_statements(self,
                         container: ProjectContainer
                         ) -> ProgramStatements:
        project = container.project
        logger.debug('finding statements for project: %s', project)

        workdir = project.directory
        command_args = ['/opt/kaskara/scripts/kaskara-statement-finder']
        command_args += project.files
        command = ' '.join(command_args)
        output_filename = os.path.join(workdir, 'statements.json')
        logger.debug('executing statement finder [%s]: %s', workdir, command)
        try:
            container.shell.check_call(command, cwd=workdir)
        except _dockerblade.CalledProcessError as err:
            msg = f'statement finder failed with code {err.returncode}'
            logger.exception(msg)
            if not project.ignore_errors:
                raise KaskaraException(msg)

        logger.debug('reading results from file: %s', output_filename)
        file_contents = container.files.read(output_filename)
        jsn: Sequence[Mapping[str, Any]] = json.loads(file_contents)
        statements = ProgramStatements.from_dict(project, jsn)
        logger.debug('finished reading results')
        return statements

    def _find_loops(self, container: ProjectContainer) -> ProgramLoops:
        project = container.project
        workdir = project.directory
        command_args = ['/opt/kaskara/scripts/kaskara-loop-finder']
        command_args += project.files
        command = ' '.join(command_args)
        output_filename = os.path.join(workdir, 'loops.json')
        logger.debug('executing loop finder [%s]: %s', workdir, command)
        try:
            container.shell.check_call(command, cwd=workdir)
        except _dockerblade.CalledProcessError as err:
            msg = f'loop finder failed with code {err.returncode}'
            logger.exception(msg)
            if not project.ignore_errors:
                raise KaskaraException(msg)

        logger.debug('reading results from file: %s', output_filename)
        file_contents = container.files.read(output_filename)
        return self._read_loops_from_file_contents(project, file_contents)

    def _read_loops_from_file_contents(self,
                                       project: Project,
                                       contents: str
                                       ) -> 'ProgramLoops':
        loop_bodies: List[FileLocationRange] = []
        jsn: Sequence[Mapping[str, str]] = json.loads(contents)
        for loop_info in jsn:
            loc = FileLocationRange.from_string(loop_info['body'])
            loc = abs_to_rel_flocrange(project.directory, loc)
            loop_bodies.append(loc)
        logger.debug('finished reading loop analysis results')
        return ProgramLoops.from_body_location_ranges(loop_bodies)

    def _find_functions(self, container: ProjectContainer) -> ProgramFunctions:
        project = container.project
        workdir = project.directory
        output_filename = os.path.join(workdir, 'functions.json')
        command_args = ['/opt/kaskara/scripts/kaskara-function-scanner']
        command_args += project.files
        command = ' '.join(command_args)

        logger.debug('executing function scanner [%s]: %s', workdir, command)
        try:
            container.shell.check_call(command, cwd=workdir)
        except _dockerblade.CalledProcessError as err:
            msg = f'function scanner failed with code {err.returncode}'
            logger.exception(msg)
            if not project.ignore_errors:
                raise KaskaraException(msg)

        logger.debug('reading results from file: %s', output_filename)
        file_contents = container.files.read(output_filename)
        jsn = json.loads(file_contents)
        functions = [FunctionDesc.from_dict(project, d) for d in jsn]
        return ProgramFunctions(functions)

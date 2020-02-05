# -*- coding: utf-8 -*-
__all__ = ('SpoonAnalyser',)

from typing import Any, Iterator, Mapping, Sequence
import contextlib
import json
import os
import shlex
import subprocess

from dockerblade import DockerDaemon as DockerBladeDockerDaemon
from loguru import logger
import attr

from .analysis import SpoonFunction, SpoonStatement
from .post_install import IMAGE_NAME as SPOON_IMAGE_NAME
from ..analyser import Analyser
from ..analysis import Analysis
from ..container import ProjectContainer
from ..functions import ProgramFunctions
from ..project import Project
from ..statements import ProgramStatements


@attr.s
class SpoonAnalyser(Analyser):
    _dockerblade: DockerBladeDockerDaemon = attr.ib(repr=False)

    @contextlib.contextmanager
    def _container(self, project: Project) -> Iterator[ProjectContainer]:
        """Provisions an ephemeral container for a given project."""
        launch = self._dockerblade.client.containers.run
        with contextlib.ExitStack() as stack:
            # create a temporary volume from the project image
            volume_name = 'kaskaraspoon'
            cmd_create_volume = (f'docker run --rm -v {volume_name}:'
                                 f'{shlex.quote(project.directory)} '
                                 f'{project.image} /bin/true')
            cmd_kill_volume = f'docker volume rm {volume_name}'
            logger.debug(f'created temporary volume [{volume_name}] '
                         f'from project image [{project.image}] '
                         f'via command: {cmd_create_volume}')
            subprocess.check_output(cmd_create_volume, shell=True)
            stack.callback(subprocess.call, cmd_kill_volume,
                           shell=True,
                           stderr=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL,
                           stdin=subprocess.DEVNULL)

            docker_analyser = launch(SPOON_IMAGE_NAME, '/bin/sh',
                                     stdin_open=True,
                                     volumes={volume_name: {
                                         'bind': '/workspace',
                                         'mode': 'ro'}},
                                     detach=True)
            stack.callback(docker_analyser.remove, force=True)

            dockerblade = self._dockerblade.attach(docker_analyser.id)
            yield ProjectContainer(project=project, dockerblade=dockerblade)

    def analyse(self, project: Project) -> Analysis:
        logger.debug(f"analysing Spoon project: {project}")
        with self._container(project) as container:
            return self._analyse_container(container)

    def _analyse_container(self, container: ProjectContainer) -> Analysis:
        dir_source = '/workspace'
        dir_output = '/output'
        container.shell.check_output(f'kaskara {dir_source} -o {dir_output}')

        # load statements
        filename_statements = os.path.join(dir_output, 'statements.json')
        statements_dict = json.loads(container.files.read(filename_statements))
        statements = self._load_statements_from_dict(statements_dict)

        # load functions
        filename_functions = os.path.join(dir_output, 'functions.json')
        functions_dict = json.loads(container.files.read(filename_functions))
        functions = self._load_functions_from_dict(functions_dict)

        raise NotImplementedError

    def _load_statements_from_dict(self,
                                   dict_: Sequence[Mapping[str, Any]]
                                   ) -> ProgramStatements:
        """Loads the statement database from a given dictionary."""
        logger.debug('parsing statements database')
        statements = \
            ProgramStatements([SpoonStatement.from_dict(d) for d in dict_])
        logger.debug(f'parsed {len(statements)} statements')
        return statements

    def _load_functions_from_dict(self,
                                  dict_: Sequence[Mapping[str, Any]]
                                  ) -> ProgramFunctions:
        """Loads the function database from a given dictionary."""
        logger.debug('parsing function database')
        functions = \
            ProgramFunctions([SpoonFunction.from_dict(d) for d in dict_])
        logger.debug(f'parsed {len(functions)} functions')
        return functions

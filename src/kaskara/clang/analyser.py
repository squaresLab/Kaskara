from __future__ import annotations

__all__ = ("ClangAnalyser",)

import json
import os
import typing as t
from typing import Any

import dockerblade as _dockerblade
from loguru import logger

from kaskara.analyser import Analyser
from kaskara.analysis import Analysis
from kaskara.clang.analysis import ClangFunction, ClangStatement
from kaskara.core import FileLocationRange
from kaskara.exceptions import KaskaraException
from kaskara.functions import ProgramFunctions
from kaskara.loops import ProgramLoops
from kaskara.statements import ProgramStatements
from kaskara.util import abs_to_rel_flocrange

if t.TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from kaskara.container import ProjectContainer
    from kaskara.project import Project


PATH_STATEMENT_FINDER = "/opt/kaskara/scripts/kaskara-statement-finder"
PATH_LOOP_FINDER = "/opt/kaskara/scripts/kaskara-loop-finder"
PATH_FUNCTION_SCANNER = "/opt/kaskara/scripts/kaskara-function-scanner"


class ClangAnalyser(Analyser):
    def analyse(self, project: Project) -> Analysis:
        logger.debug(f"analysing Clang project: {project}")
        with project.provision() as container:
            return self._analyse_container(container)

    def _analyse_container(
        self,
        container: ProjectContainer,
    ) -> Analysis:
        loops = self._find_loops(container)
        functions = self._find_functions(container)
        statements = self._find_statements(container)
        insertions = statements.insertions()
        return Analysis(
            project=container.project,
            loops=loops,
            functions=functions,
            statements=statements,
            insertions=insertions,
        )

    def _execute_command(
        self,
        container: ProjectContainer,
        command_args: list[str],
        output_filename: str,
        *,
        analysis_name: str | None = None,
    ) -> t.Any:  # noqa: ANN401
        project = container.project
        workdir = project.directory

        driver = command_args[0]
        assert os.path.isabs(driver)
        if not container.files.exists(driver):
            error_message = f"driver {driver} does not exist"
            raise KaskaraException(error_message)

        if not os.path.isabs(output_filename):
            output_filename = os.path.join(workdir, output_filename)

        command_args += ["2>1"]
        command = " ".join(command_args)

        logger.debug(f"executing {analysis_name} [{workdir}]: {command}")

        analysis_name = analysis_name or output_filename
        maybe_error_message: str | None = None
        maybe_error: Exception | None = None
        output: str = ""
        try:
            output = container.shell.check_output(command, cwd=workdir, text=True)
        except _dockerblade.CalledProcessError as err:
            maybe_error = err
            output = err.output
            assert isinstance(output, str)
            maybe_error_message = f"failed with exit code {err.returncode}: {output}"

        analysis_completed = container.files.exists(output_filename)

        if not analysis_completed:
            message = f"{analysis_name}: failed to produce output"
            if maybe_error:
                message = f"{message}: {maybe_error_message}"
                raise KaskaraException(message) from maybe_error
            raise KaskaraException(message)

        if analysis_completed and maybe_error_message:
            message = f"{analysis_name}: completed with errors:\n{maybe_error_message}"
            logger.warning(message)

        output = container.files.read(output_filename)
        return json.loads(output)

    def _find_statements(
        self,
        container: ProjectContainer,
    ) -> ProgramStatements:
        project = container.project
        logger.debug(f"finding statements for project: {project}")

        command_args = [PATH_STATEMENT_FINDER]
        command_args += sorted(project.files)
        output_filename = "statements.json"

        output_jsn: Sequence[Mapping[str, Any]] = self._execute_command(
            container=container,
            command_args=command_args,
            output_filename=output_filename,
            analysis_name="statement finder",
        )
        statements = ProgramStatements(
            [ClangStatement.from_dict(project, d) for d in output_jsn],
        )
        logger.debug("finished reading results")
        return statements

    def _find_loops(
        self,
        container: ProjectContainer,
    ) -> ProgramLoops:
        project = container.project
        command_args = [PATH_LOOP_FINDER]
        command_args += sorted(project.files)
        output_filename = "loops.json"

        output_jsn = self._execute_command(
            container=container,
            command_args=command_args,
            output_filename=output_filename,
            analysis_name="loop finder",
        )

        return self._read_loops_from_jsn(project, output_jsn)

    def _read_loops_from_jsn(
        self,
        project: Project,
        jsn: Sequence[Mapping[str, str]],
    ) -> ProgramLoops:
        loop_bodies: list[FileLocationRange] = []
        for loop_info in jsn:
            loc = FileLocationRange.from_string(loop_info["body"])
            loc = abs_to_rel_flocrange(project.directory, loc)
            loop_bodies.append(loc)
        logger.debug("finished reading loop analysis results")
        return ProgramLoops.from_body_location_ranges(loop_bodies)

    def _find_functions(
        self,
        container: ProjectContainer,
    ) -> ProgramFunctions:
        project = container.project
        output_filename = "functions.json"
        command_args = [PATH_FUNCTION_SCANNER]
        command_args += sorted(project.files)

        output_jsn = self._execute_command(
            container=container,
            command_args=command_args,
            output_filename=output_filename,
            analysis_name="function scanner",
        )

        return ProgramFunctions.from_functions(
            project=project,
            functions=(ClangFunction.from_dict(project, d) for d in output_jsn),
        )

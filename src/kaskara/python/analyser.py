__all__ = ("PythonAnalyser",)

from loguru import logger

from kaskara.analyser import Analyser
from kaskara.analysis import Analysis
from kaskara.container import ProjectContainer
from kaskara.project import Project
from kaskara.python.functions import collect_functions
from kaskara.python.loops import collect_loops
from kaskara.python.statements import collect_statements


class PythonAnalyser(Analyser):
    def analyse(self, project: Project) -> Analysis:
        logger.debug(f"analysing Python project: {project}")
        with project.provision() as container:
            return self._analyse_container(container)

    def _analyse_container(self, container: ProjectContainer) -> Analysis:
        functions = collect_functions(container)
        statements = collect_statements(container)
        loops = collect_loops(container)
        insertions = statements.insertions()
        return Analysis(
            project=container.project,
            functions=functions,
            statements=statements,
            insertions=insertions,
            loops=loops,
        )

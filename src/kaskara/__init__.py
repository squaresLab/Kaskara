from loguru import logger as _logger

from . import clang, python, spoon
from .analyser import Analyser
from .analysis import Analysis
from .exceptions import KaskaraException
from .insertions import InsertionPoint
from .loops import ProgramLoops
from .post_install import post_install
from .project import Project
from .statements import Statement
from .version import __version__

_logger.disable("kaskara")

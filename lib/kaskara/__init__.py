# -*- coding: utf-8 -*-
from loguru import logger as _logger

from .version import __version__
from .exceptions import KaskaraException
from .project import Project
from .analysis import Analysis
from .analyser import Analyser
from .insertions import InsertionPoint
from .statements import Statement
from .loops import ProgramLoops
from .post_install import post_install
from . import clang
from . import python


_logger.disable('kaskara')

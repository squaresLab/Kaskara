# -*- coding: utf-8 -*-
import logging

from .version import __version__
from .exceptions import KaskaraException
from .project import Project
from .analysis import Analysis
from .analyser import Analyser
from .insertions import InsertionPoint
from .statements import Statement
from .loops import ProgramLoops

from . import clang

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

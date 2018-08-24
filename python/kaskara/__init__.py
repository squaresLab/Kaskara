import logging

from .version import __version__
from .exceptions import BondException
from .analysis import Analysis
from .insertions import InsertionPoint
from .statements import Statement

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

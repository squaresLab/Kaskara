# -*- coding: utf-8 -*-
__all__ = ('PythonFunction', 'PythonStatement')

from typing import Sequence, Optional, FrozenSet

import attr

from ..core import FileLocationRange
from ..functions import Function
from ..statements import Statement


@attr.s(frozen=True, auto_attribs=True, slots=True)
class PythonFunction(Function):
    name: str
    location: FileLocationRange
    body_location: FileLocationRange

    @property
    def return_type(self) -> Optional[str]:
        return None


@attr.s(frozen=True, auto_attribs=True, slots=True)
class PythonStatement(Statement):
    kind: str
    content: str
    canonical: str
    location: FileLocationRange

    @property
    def visible(self) -> Optional[FrozenSet[str]]:
        return None

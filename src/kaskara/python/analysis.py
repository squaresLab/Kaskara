from __future__ import annotations

__all__ = ("PythonFunction", "PythonStatement")

import typing as t

import attr

from kaskara.functions import Function
from kaskara.statements import Statement

if t.TYPE_CHECKING:
    from kaskara.core import FileLocationRange


@attr.s(frozen=True, auto_attribs=True, slots=True)
class PythonFunction(Function):
    name: str
    location: FileLocationRange
    body_location: FileLocationRange

    @property
    def return_type(self) -> str | None:
        return None


@attr.s(frozen=True, auto_attribs=True, slots=True)
class PythonStatement(Statement):
    kind: str
    content: str
    canonical: str
    location: FileLocationRange

    @property
    def visible(self) -> frozenset[str] | None:
        return None

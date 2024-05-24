__all__ = ("PythonFunction", "PythonStatement")


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

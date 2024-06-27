from __future__ import annotations

__all__ = ("SpoonFunction", "SpoonStatement")

import typing as t

import attr
from overrides import overrides

from kaskara.core import FileLocationRange
from kaskara.functions import Function
from kaskara.statements import Statement

if t.TYPE_CHECKING:
    from collections.abc import Mapping


@attr.s(frozen=True, slots=True, auto_attribs=True)
class SpoonFunction(Function):
    name: str
    location: FileLocationRange
    body_location: FileLocationRange
    return_type: str

    @overrides
    def to_dict(self) -> dict[str, t.Any]:
        return {
            "name": self.name,
            "location": str(self.location),
            "body": str(self.body_location),
            "return-type": self.return_type,
        }

    @classmethod
    def from_dict(cls, dict_: Mapping[str, t.Any]) -> t.Self:
        name: str = dict_["name"]
        location = FileLocationRange.from_string(dict_["location"])
        body_location = FileLocationRange.from_string(dict_["body"])
        return_type = dict_["return-type"]
        return cls(
            name=name,
            location=location,
            body_location=body_location,
            return_type=return_type,
        )


@attr.s(frozen=True, auto_attribs=True, slots=True)
class SpoonStatement(Statement):
    kind: str
    content: str
    canonical: str
    location: FileLocationRange

    @classmethod
    def from_dict(cls, dict_: Mapping[str, t.Any]) -> t.Self:
        kind: str = dict_["kind"]
        content: str = dict_["source"]
        canonical: str = dict_["canonical"]
        location = FileLocationRange.from_string(dict_["location"])
        return cls(
            kind=kind,
            content=content,
            canonical=canonical,
            location=location,
        )

    @property
    def visible(self) -> frozenset[str] | None:
        return None

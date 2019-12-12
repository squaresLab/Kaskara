__all__ = ('ClangAnalysis',)

import json

from .analysis import Analysis


class ClangAnalysis(Analysis):
    @classmethod
    def from_file(cls, filename: str) -> 'Analysis':
        with open(filename, 'r') as f:
            dict_ = json.load(f)
        return Analysis.from_dict(dict_, snapshot)

    def to_file(self, filename: str) -> None:
        raise NotImplementedError

from typing import FrozenSet, Dict, Any


@attr.s(frozen=True)
class Statement(object):
    content = attr.ib(type=str)
    location = attr.ib(type=FileLocationRange)
    reads = attr.ib(type=FrozenSet[str])
    writes = attr.ib(type=FrozenSet[str])

    @staticmethod
    def from_dict(d: Dict[str, Any], snapshot: Snapshot) -> 'Statement':
        # FIXME
        location = FileLocationRange.from_string(d['location'])
        location = abs_to_rel_flocrange(snapshot.source_dir, location)
        return Statement(d['content'],
                         location,
                         frozenset(d['reads']),
                         frozenset(d['writes']))

    def to_dict(self, snapshot: Snapshot) -> Dict[str, Any]:
        loc = rel_to_abs_flocrange(snapshot.source_dir, self.location)
        return {'content': self.content,
                'location': str(loc),
                'reads': [v for v in self.reads],
                'writes': [v for v in self.writes]}

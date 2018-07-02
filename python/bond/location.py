__all__ ['FileLocation', 'FileLocationRange']

from typing import Dict, List, Iterable

from boggart.core.location import FileLocation, FileLocationRange


class FileLocationRangeSet(object):
    def __init__(self, ranges: Iterable[FileLocationRange]) -> None:
        self.__fn_to_ranges = {}  # type: Dict[str, List[FileLocationRange]]
        for r in ranges:
            if r.filename not in self.__fn_to_ranges:
                self.__fn_to_ranges[r.filename] = []
            self.__fn_to_ranges[r.filename].append(r)

    def __contains__(self, location: FileLocation) -> bool:
        ranges = self.__fn_to_ranges.get(location.filename, [])
        return any(location in r for r in ranges)

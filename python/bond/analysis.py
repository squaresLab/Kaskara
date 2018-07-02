from typing import List

from .location import FileLocation, FileLocationRange, FileLocationRangeSet


class Analysis(object):
    def __init__(self,
                 loop_bodies: List[FileLocationRange],
                 function_bodies: List[FileLocationRange]
                 ) -> None:
        self.__location_bodies = FileLocationRangeSet(loop_bodies)
        self.__location_functions = FileLocationRangeSet(function_bodies)

    def is_inside_loop(self, location: FileLocation) -> bool:
        return location in self.__location_bodies

    def is_inside_function(self, location: FileLocation) -> bool:
        return location in self.__location_functions

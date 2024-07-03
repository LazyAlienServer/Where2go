import random, re
from typing import Any, Union
from typing import TypedDict


class WaypointDict(TypedDict):
    pos: tuple
    dimension: int
    name: str
    title: str
    color: str


class Waypoint:

    def __init__(self, pos: tuple, dimension: int, name: str, title: str = None, color: Union[int,str] = None) -> None:
        '''Create a waypoint

Parameters
----
pos : tuple (pos_x: int, pox_y: int, pox_z: int)

dimension : int
  0: overworld
  1: the_nether
  2: the_end

name : str
  The name of the waypoint

color : int | str
  0-9 | a-f
  A minecraft formatting code representing the color of the waypoint
  If None, randomly generate'''

        self.pos: tuple = pos
        self.dimension: int = dimension
        self.name: str = name
        if not title:
            title = name[0]
        self.title: str = title
        color = str(color)
        formatting_codes = "0123456789abcdef"
        if len(color) != 1 or color not in formatting_codes:
            color = random.choice(formatting_codes)
        self.color: str = color
    

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Waypoint) and self.pos == __value.pos
    

    def is_close_to(self, pos: tuple, distance: int):
        return sum([(i-k)**2 for i,k in zip(self.pos, pos)]) <= distance**2


    def to_dict(self) -> WaypointDict:
        return {
            "pos": self.pos,
            "dimension": self.dimension,
            "name": self.name,
            "title": self.title,
            "color": self.color
        }


    def transform_xaero_waypoint(content: str, dimensions_map = {"Internal-overworld-waypoints":0, "Internal-the-nether-waypoints":1, "Internal-the-end-waypoints":2}):
        # xaero-waypoint:NAME:TITLE:X:Y:Z:COLOR:false:0:DIMENSION
        result = re.fullmatch("xaero-waypoint:(.+):(.+):(-?[0-9]+):(-?[0-9]+):(-?[0-9]+):([0-9]{0,2}):.+:(.+)")
        if not result:
            return
        name, title, x, y, z, color, dimension = result.groups()
        if dimension not in dimensions_map:
            return
        dimension = dimensions_map[dimension]
        return Waypoint((x, y, z), dimension, name, title, color)
    

    def get_xaero_waypoint(self, dimensions_map = {0:"Internal-overworld-waypoints", 1:"Internal-the-nether-waypoints", 2:"Internal-the-end-waypoints"}):
        return f"xaero-waypoint:{self.name}:{self.title}:{':'.join(self.pos)}:{self.color}:false:0:{dimensions_map[self.dimension]}"
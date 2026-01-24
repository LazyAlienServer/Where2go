from typing import TypedDict, Union, List, Literal, Optional
from where2go.utils.waypoints.waypoint import Waypoint

class WaypointData(TypedDict):
    id: str
    create_time: str
    creator: str
    waypoint: Waypoint
    link: Optional[str]


ClickEventStyleValue = Literal["old", "new"]
ClickEventFormat = Union[ClickEventStyleValue, List[ClickEventStyleValue]]
ClickEventStyleParameter = Union[ClickEventFormat, Literal["default"]]
from mcdreforged.api.rtext import RTextList, RText, RColor, RAction
from .waypoint import Waypoint
from where2go.utils.display_utils import rtr
from where2go.utils.waypoints.constants import FORMATTING_CODES
from typing import List, Union, Literal
from mcdreforged.api.all import ServerInterface

CLICK_EVENT_FORMAT = Union[List[Literal["old", "new"]], Literal["old", "new"]]

class Display:

    _click_event_format: CLICK_EVENT_FORMAT = "old"

    def configure(click_event_format: CLICK_EVENT_FORMAT = "old", ):
        Display._click_event_format = click_event_format

    def transform(waypoint: Waypoint):
        x, y, z = waypoint.pos
        match waypoint.dimension:
            case "overworld":
                trans_waypoint = Waypoint((x//8, y, z//8), "the_nether", waypoint.name, waypoint.title, waypoint.color)
                return RTextList("§8 -> ", Display.pos(trans_waypoint), " ", Display.xaero_click_event(trans_waypoint))
            case "the_nether":
                trans_waypoint = Waypoint((x*8, y, z*8), "overworld", waypoint.name, waypoint.title, waypoint.color)
                return RTextList("§8 -> ", Display.pos(trans_waypoint), " ", Display.xaero_click_event(trans_waypoint))
        return ""

    def show(waypoint: Waypoint, id=None):
        title = rtr("waypoints.display.show", name=waypoint.name)
        if id:
            title = title.h(rtr("waypoints.display.id", id=id))
        return RTextList(title, " ", Display.pos(waypoint), " ", Display.xaero_click_event(waypoint), Display.transform(waypoint))
    
    def temporary(waypoint: Waypoint, command_prefix):
        return RTextList(
            rtr("waypoints.display.temporary", name=waypoint.name), 
            " ", 
            Display.pos(waypoint), 
            " ", 
            Display.xaero_click_event(waypoint), 
            Display.transform(waypoint), 
            " ", 
            Display.temporary_click_event(waypoint, command_prefix)
        )
    
    def pos(waypoint: Waypoint) -> str:
        x, y, z = waypoint.pos
        return rtr(f"waypoints.display.pos.{waypoint.dimension}", x=x, y=y, z=z)
    
    def xaero_click_event(waypoint: Waypoint, style = "default") -> Union[RText, RTextList]:
        style = Display._click_event_format if style == "default" else style
        if isinstance(style, list):
            # Insert a space between each click event when multiple styles are requested
            parts = []
            for s in style:
                parts.append(Display.xaero_click_event(waypoint, s))
                parts.append(" ")
            parts.pop()  # remove trailing space
            return RTextList(*parts)
        if style not in ["old", "new"]:
            raise ValueError("Invalid style")
        return RText("[+X]", color=RColor.gold if style == "old" else RColor.yellow).c(
                RAction.run_command, 
                Display.get_xaero_waypoint_add(waypoint, style)
            ).h(RTextList(
                rtr("waypoints.display.hover_text.xaero"),
                RText("\n"),
                rtr("waypoints.display.hover_text.xaero_{style}".format(style=style)
            )))

    def temporary_click_event(waypoint: Waypoint, command_prefix) -> RText:
        return RText("[+]", color=RColor.green).c(
            RAction.run_command, 
            f"{command_prefix} add {waypoint.get_xaero_waypoint()}"
        ).h(rtr("waypoints.display.hover_text.temporary").set_color(RColor.green))

    def get_xaero_waypoint_add(waypoint: Waypoint, style: str) -> str:
        text = f"xaero_waypoint_add:{waypoint.name}:{waypoint.title}:{':'.join(map(str,waypoint.pos))}:{FORMATTING_CODES.index(waypoint.color)}:false:0:"
        match style:
            case "old":
                text = text + f"Internal_{waypoint.dimension}_waypoints"
            case "new":
                text = text + f"Internal-{waypoint.dimension}"
            case _:
                raise ValueError("Invalid style")
        return text
    
    def waypoint_error():
        return rtr("waypoints.display.error")
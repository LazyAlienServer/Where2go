from mcdreforged.api.all import RText, RTextBase, RTextList, RColor, RAction, RTextTranslation, RStyle
from where2go.utils.waypoints.waypoint import Waypoint
from where2go.utils.display_utils import rtr
from where2go.utils.waypoints.constants import FORMATTING_CODES
from where2go.utils.waypoints.types import ClickEventFormat, ClickEventStyleParameter, WaypointData
from typing import Union, Literal, Optional, List


NETHER_SCALE = 8


class RTextButton(RText):

    def __init__(self, button_text: str, button_color: RColor, click_command: str, hover_text: RTextBase):
        super().__init__(button_text, color=button_color)
        self.c(RAction.run_command, click_command).h(hover_text)


class RTextXaeroButton(RTextButton): # for adding waypoints to Xaero's Minimap

    def __init__(self, waypoint: Waypoint, style: Literal["old", "new"]):
        match style:
            case "old":
                button_color = RColor.gold
            case "new":
                button_color = RColor.yellow
            case _:
                raise ValueError("Invalid style")
        click_command = self._xaero_waypoint_add_text(waypoint, style)
        hover_text = RTextList(
            rtr("waypoints.display.hover_text.xaero"),
            RText("\n"),
            rtr(f"waypoints.display.hover_text.xaero_{style}")
        )
        super().__init__("[+X]", button_color, click_command, hover_text)

    def _xaero_waypoint_add_text(self, waypoint: Waypoint, style: str) -> str:
        text = f"xaero_waypoint_add:{waypoint.name}:{waypoint.title}:{':'.join(map(str,waypoint.pos))}:{FORMATTING_CODES.index(waypoint.color)}:false:0:"
        match style:
            case "old":
                text = text + f"Internal_{waypoint.dimension}_waypoints"
            case "new":
                text = text + f"Internal-{waypoint.dimension}"
            case _:
                raise ValueError("Invalid style")
        return text


class RTextTemporaryButton(RTextButton): # for adding temporary waypoints to sharing waypoints

    def __init__(self, waypoint: Waypoint, command_prefix: str):
        button_color = RColor.green
        click_command = f"{command_prefix} add {waypoint.get_xaero_waypoint()}"
        hover_text = rtr("waypoints.display.hover_text.temporary").set_color(RColor.green)
        super().__init__("[+]", button_color, click_command, hover_text)


class RTextLinkButton(RTextButton): # for linking two waypoints

    def __init__(self, id1: str, id2: str, command_prefix: str):
        button_color = RColor.aqua
        click_command = f"{command_prefix} link {id1} {id2}"
        hover_text = rtr("waypoints.display.hover_text.link", id=id1, target_id=id2).set_color(RColor.aqua)
        super().__init__("[+⇄]", button_color, click_command, hover_text)


class RTextWaypoint(RTextList):

    _command_prefix: str = "!!wp"
    _click_event_format: ClickEventFormat = "old"

    @staticmethod
    def configure(
            command_prefix: str,
            click_event_format: ClickEventFormat
        ):
        RTextWaypoint._command_prefix = command_prefix
        RTextWaypoint._click_event_format = click_event_format

    def __init__(
            self,
            waypoint: Waypoint,
            linked_waypoint_parameter: Union[bool, Waypoint]=True,
            id: str=None,
            linked_id: str=None,
            is_temporary: bool=False,
            has_title: bool=True,
            has_xaero_button: bool=True,
            has_temporary_button: bool=True,
            has_link_button: bool=False,
            display_name: bool=True,
        ):

        self.waypoint = waypoint
        has_link_button = has_link_button and id and linked_id

        parts = [self._pos_text()]
        if display_name:
            parts = [waypoint.name, " "] + parts
        if RTextWaypoint._click_event_format and has_xaero_button:
            parts = parts + [" ", self._xaero_click_button(RTextWaypoint._click_event_format)]
        if has_title:
            parts = [self._title_text(id, linked_id, is_temporary), " "] + parts
        linked_waypoint_parameter = self._linked_waypoint_text(linked_waypoint_parameter, linked_id, has_link_button)
        if linked_waypoint_parameter:
            parts = parts + [" ", linked_waypoint_parameter]
        if is_temporary and has_temporary_button:
            parts = parts + [" ", RTextTemporaryButton(waypoint, RTextWaypoint._command_prefix)]
        if has_link_button:
            parts = parts + [" ", RTextLinkButton(id, linked_id, RTextWaypoint._command_prefix)]
        super().__init__(*parts)

    def _title_text(self, id: Optional[str] = None, linked_id: Optional[str] = None, is_temporary: Optional[bool] = None) -> RTextBase:
        if is_temporary:
            return rtr("waypoints.display.temporary")
        title = rtr("waypoints.display.default_title")
        if not id: # a waypoint with an ID is not temporary
            return title
        if linked_id:
            return title.h(rtr("waypoints.display.link", id=id, target_id=linked_id))
        return title.h(rtr("waypoints.display.id", id=id))

    def _pos_text(self) -> str:
        x, y, z = self.waypoint.pos
        return rtr(f"waypoints.display.pos.{self.waypoint.dimension}", x=x, y=y, z=z)
    
    def _xaero_click_button(self, style: ClickEventStyleParameter = "default") -> Union[RText, RTextList]:
        style = RTextWaypoint._click_event_format if style == "default" else style
        if isinstance(style, List):
            if not style:
                raise ValueError("Style list cannot be empty")
            parts = []
            for s in style:
                parts.append(RTextXaeroButton(self.waypoint, s))
                parts.append(" ")
            parts.pop()  # remove trailing space
            return RTextList(*parts)
        if style not in ["old", "new"]:
            raise ValueError("Invalid style")
        return RTextXaeroButton(self.waypoint, style)

    def _linked_waypoint_text(self, linked_waypoint_parameter: Union[bool, Waypoint], linked_id: str = None, has_link_button: bool = False) -> Optional[RTextList]:
        if linked_waypoint_parameter is False:
            return None
        if linked_waypoint_parameter is True:
            waypoint = self.waypoint
            x, y, z = waypoint.pos
            match waypoint.dimension:
                case "overworld":
                    trans_pos, trans_dimension = (x//NETHER_SCALE, y, z//NETHER_SCALE), "the_nether"
                case "the_nether":
                    trans_pos, trans_dimension = (x*NETHER_SCALE, y, z*NETHER_SCALE), "overworld"
                case "the_end":
                    return None
                case _:
                    raise ValueError(f"Cannot transform waypoint in '{waypoint.dimension}' dimension")
            linked_waypoint = Waypoint(trans_pos, trans_dimension, waypoint.name, waypoint.title, waypoint.color)
            linker = "§8-> "
        elif isinstance(linked_waypoint_parameter, Waypoint):
            linked_waypoint = linked_waypoint_parameter
            linker = "§7⇆ " if has_link_button else "§b⇆ "
        else:
            raise ValueError("linked_waypoint_parameter can only be True, False or a Waypoint instance")    
        return RTextList(
            linker, 
            RTextWaypoint(
                waypoint=linked_waypoint,
                linked_waypoint_parameter=False,
                id=linked_id,
                has_title=False,
                has_xaero_button=not has_link_button,
                display_name=linked_waypoint_parameter is not True
            )
        )


class RTextWaypointSimple(RTextWaypoint):

    def __init__(self, waypoint_data: WaypointData, linked_waypoint_data: Optional[WaypointData] = None, **kwargs):
        linked_id = linked_waypoint_data["id"] if linked_waypoint_data else None
        trans_waypoint = linked_waypoint_data["waypoint"] if linked_waypoint_data else kwargs.get("trans_waypoint", True)
        super().__init__(
            waypoint_data["waypoint"],
            linked_waypoint_parameter=trans_waypoint,
            id=waypoint_data["id"], 
            linked_id=linked_id,
            **kwargs
        )


class RTextWaypointError(RText):
    
    def __init__(self):
        error_text = rtr("waypoints.display.error")
        super().__init__(error_text)
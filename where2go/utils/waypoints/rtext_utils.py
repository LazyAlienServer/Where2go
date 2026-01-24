from mcdreforged.api.all import RText, RTextBase, RTextList, RColor, RAction, RTextTranslation
from where2go.utils.waypoints.waypoint import Waypoint
from where2go.utils.display_utils import rtr
from where2go.utils.waypoints.constants import FORMATTING_CODES
from where2go.utils.waypoints.types import ClickEventFormat, ClickEventStyleParameter
from typing import Union, Literal, Optional, List


class RTextButton(RText):

    def __init__(self, button_text: str, button_color: RColor, click_command: str, hover_text: RTextBase):
        super().__init__(button_text, color=button_color)
        self.c(RAction.run_command, click_command).h(hover_text)


class RTextXaeroButton(RTextButton):

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


class RTextTemporaryButton(RTextButton):

    def __init__(self, waypoint: Waypoint, command_prefix: str):
        button_color = RColor.green
        click_command = f"{command_prefix} add {waypoint.get_xaero_waypoint()}"
        hover_text = rtr("waypoints.display.hover_text.temporary").set_color(RColor.green)
        super().__init__("[+]", button_color, click_command, hover_text)


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
            id: str=None,
            is_temporary: bool=False,
            has_title: bool=True,
            trans_waypoint: Union[bool, Waypoint]=True
        ):

        self.waypoint = waypoint

        parts = [self._pos_text()]
        if RTextWaypoint._click_event_format:
            parts = parts + [" ", self._xaero_click_button(RTextWaypoint._click_event_format)]
        if has_title:
            parts = [self._title_text(id, is_temporary), " "] + parts
        if trans_waypoint is not False:
            parts = parts + [" ", self._trans_waypoint_text(trans_waypoint)]
        if is_temporary:
            parts = parts + [" ", RTextTemporaryButton(waypoint, RTextWaypoint._command_prefix)]
        super().__init__(*parts)

    def _title_text(self, id: Optional[str] = None, is_temporary: Optional[bool] = None) -> RTextBase:
        if is_temporary:
            return rtr("waypoints.display.temporary", name=self.waypoint.name)
        title = rtr("waypoints.display.show", name=self.waypoint.name)
        if id: # a waypoint with an ID is not temporary
            title = title.h(rtr("waypoints.display.id", id=id))
        return title

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

    def _trans_waypoint_text(self, trans_waypoint: Union[bool, Waypoint]) -> RTextList:
        if not trans_waypoint:
            raise ValueError("trans_waypoint can only be True or a Waypoint instance")
        if trans_waypoint is True:
            waypoint = self.waypoint
            x, y, z = waypoint.pos
            match waypoint.dimension:
                case "overworld":
                    trans_pos, trans_dimension = (x//8, y, z//8), "the_nether"
                case "the_nether":
                    trans_pos, trans_dimension = (x*8, y, z*8), "overworld"
                case _:
                    raise ValueError(f"Cannot transform waypoint in '{waypoint.dimension}' dimension")
            trans_waypoint = Waypoint(trans_pos, trans_dimension, waypoint.name, waypoint.title, waypoint.color)
            linker = "§8-> "
        else:
            linker = " §8<=> "
        return RTextList(linker, RTextWaypoint(trans_waypoint, has_title=False, trans_waypoint=False))


class RTextWaypointError(RText):
    
    def __init__(self):
        error_text = rtr("waypoints.display.error")
        super().__init__(error_text)
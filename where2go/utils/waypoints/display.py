from mcdreforged.api.rtext import RTextList, RText, RColor, RAction
from .waypoint import Waypoint
from where2go.utils.display_utils import rtr

class Display:

    def transform(waypoint: Waypoint):
        x, y, z = waypoint.pos
        if waypoint.dimension == "overworld":
            trans_waypoint = Waypoint((x//8, y, z//8), "the_nether", waypoint.name, waypoint.title, waypoint.color)
            return RTextList("§8 -> ", Display.pos(trans_waypoint), " ", Display.xaero_click_event(trans_waypoint))
        elif waypoint.dimension == "the_nether":
            trans_waypoint = Waypoint((x*8, y, z*8), "overworld", waypoint.name, waypoint.title, waypoint.color)
            return RTextList("§8 -> ", Display.pos(trans_waypoint), " ", Display.xaero_click_event(trans_waypoint))
        return ""

    def show(waypoint: Waypoint, id=None):
        title = rtr("waypoints.display.show", name=waypoint.name)
        if id:
            title = title.h(rtr("waypoints.display.id", id=id))
        return RTextList(title, " ", Display.pos(waypoint), " ", Display.xaero_click_event(waypoint), Display.transform(waypoint))
    
    def temporary(waypoint: Waypoint, command_prefix):
        return RTextList(rtr("waypoints.display.temporary", name=waypoint.name), " ", Display.pos(waypoint), " ", Display.xaero_click_event(waypoint), Display.transform(waypoint), " ", Display.temporary_click_event(waypoint, command_prefix))
    
    def pos(waypoint: Waypoint) -> str:
        x, y, z = waypoint.pos
        return rtr(f"waypoints.display.pos.{waypoint.dimension}", x=x, y=y, z=z)
    
    def xaero_click_event(waypoint: Waypoint) -> RText:
        return RText("[+X]", color=RColor.gold).c(RAction.run_command, waypoint.get_xaero_waypoint_add()).h(rtr("waypoints.display.hover_text.xaero").set_color(RColor.gold))
    
    def temporary_click_event(waypoint: Waypoint, command_prefix) -> RText:
        return RText("[+]", color=RColor.green).c(RAction.run_command, f"{command_prefix} add {waypoint.get_xaero_waypoint()}").h(rtr("waypoints.display.hover_text.temporary").set_color(RColor.green))
    
    def waypoint_error():
        return rtr("waypoints.display.error")
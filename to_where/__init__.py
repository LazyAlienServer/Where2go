from mcdreforged.api.all import PluginServerInterface, CommandSource, CommandContext
from to_where.utils.waypoints import WaypointManager, Waypoint, Display
from to_where.utils.api import PlayerAPI
from to_where.constants import DEFAULT_CONFIG

class Proxy:

    def __init__(self, server: PluginServerInterface) -> None:
        config = server.load_config_simple("config.json", default_config=DEFAULT_CONFIG)
        self.waypoint_manager = WaypointManager()
        self.api = PlayerAPI(config["player_api"])
        self.display = Display(config["display"])
    
    def add(self, source: CommandSource, context: CommandContext):
        waypoint : Waypoint = Waypoint.transform_xaero_waypoint(context["waypoint"])
        creater = source.player if source.is_player else "[Server]"
        if waypoint:
            self.waypoint_manager.add(creater, waypoint)
            source.reply(self.display.show(waypoint))
        else:
            source.reply(self.display.waypoint_error())
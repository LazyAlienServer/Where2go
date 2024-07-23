from mcdreforged.api.all import PluginServerInterface, PluginCommandSource, CommandSource, CommandContext, Info, new_thread, SimpleCommandBuilder, Text, Integer, RText, RTextList, RAction, RColor
from where2go.utils.waypoints import WaypointManager, Waypoint, Display
from where2go.utils.api import PlayerAPI
from where2go.utils.display_utils import rtr, help_msg
from where2go.constants import DEFAULT_CONFIG, PLUGIN_ID
import re


class Proxy:

    def __init__(self, server: PluginServerInterface) -> None:
        self.config = server.load_config_simple("config.json", default_config=DEFAULT_CONFIG)
        self.waypoint_manager = WaypointManager(server)
        self.api = PlayerAPI(self.config["player_api"])

        prefix = self.config["command"]["waypoints"]
        self.prefix = prefix
        builder = SimpleCommandBuilder()
        builder.command(f"{prefix}", self.help_msg) # wp help
        builder.command(f"{prefix} help", self.help_msg)
        builder.arg("waypoint", Text) # wp add
        builder.command(f"{prefix} add", lambda source, context: source.reply(help_msg("add", prefix)))
        builder.command(f"{prefix} add <waypoint>", self.add)
        builder.command(f"{prefix} forceadd <waypoint>", lambda source, context: self.add(source, context, True))
        builder.arg("id", Text) # wp remove
        builder.command(f"{prefix} remove", lambda source, context: source.reply(help_msg("remove", prefix)))
        builder.command(f"{prefix} remove <id>", self.remove)
        builder.command(f"{prefix} info", lambda source, context: source.reply(help_msg("info", prefix)))
        builder.command(f"{prefix} info <id>", self.info)
        builder.arg("page", Text) # wp list
        builder.command(f"{prefix} list", self.list)
        builder.command(f"{prefix} list <page>", self.list)
        builder.arg("name", Text) # wp search
        builder.command(f"{prefix} search", lambda source, context: source.reply(help_msg("search", prefix)))
        builder.command(f"{prefix} search <name>", self.search)
        here_prefix = self.config['command']['here'] # here
        builder.command(f"{here_prefix}", lambda source, context: self.player_pos(source, context, source.player) if source.is_player else None)
        builder.arg("player", Text)
        whereis_prefix = self.config['command']['whereis'] # vris
        builder.command(f"{whereis_prefix}", lambda source, context: source.reply(RTextList(RText(f"§7{whereis_prefix} <player>").c(RAction.suggest_command, f"{whereis_prefix}"), " ", rtr(f"help.whereis"))))
        builder.command(f"{whereis_prefix} <player>", lambda source, context: self.player_pos(source, context, context["player"]))
        builder.register(server)

        server.register_help_message(prefix, rtr("help.wp"))
        server.register_help_message(here_prefix, rtr("help.here"))
        server.register_help_message(whereis_prefix, rtr("help.whereis"))
        server.register_help_message(self.config["command"]["fastsearch_prompt"], rtr("help.fastsearch", prompt=self.config["command"]["fastsearch_prompt"]))
    

    def help_msg(self, source: CommandSource, context: CommandContext):
        for i in ["add", "remove", "list", "search", "info"]:
            source.reply(help_msg(i, self.prefix))


    def add(self, source: CommandSource, context: CommandContext, force=False):
        waypoint : Waypoint = Waypoint.transform_xaero_waypoint(context["waypoint"])
        creater = source.player if source.is_player else "[Server]"
        if not waypoint:
            source.reply(Display.waypoint_error())
            return
        search = self.waypoint_manager.search_distance(waypoint.pos, waypoint.dimension, 0)
        if search:
            search = search[0]
            source.reply(rtr("command.add.fail.waypoint_exist"))
            source.reply(Display.show(search["waypoint"], search["id"]))
            return
        search = self.waypoint_manager.search_distance(waypoint.pos, waypoint.dimension, 32)
        if not force and search:
            source.reply(RTextList(rtr("command.add.fail.waypoint_close"), " ", rtr("command.add.fail.forceadd").c(RAction.run_command, f"{self.prefix} forceadd {context['waypoint']}")))
            for i in search:
                source.reply(RTextList("%.1fm "%waypoint.distance(i["waypoint"].pos), Display.show(i["waypoint"], i["id"])))
            return
        data = self.waypoint_manager.add(creater, waypoint)
        source.reply(rtr("command.add.success", id=data["id"]))
        source.reply(Display.show(waypoint, data["id"]))
            
    
    def remove(self, source: CommandSource, context: CommandContext):
        waypoint = self.waypoint_manager.remove(context["id"])
        if waypoint:
            source.reply(rtr("command.remove.success"))
            source.reply(Display.show(waypoint["waypoint"]))
        else:
            source.reply(rtr("command.remove.fail"))
    

    def list(self, source: CommandSource, context: CommandContext):
        if "page" in context.keys():
            page = context["page"]
            if not re.fullmatch("[0-9]+", page):
                source.reply(rtr("command.list.page_error"))
                return
            page = int(page)
        else:
            page = 1
        page = int(page)
        data = self.waypoint_manager.data
        total = (len(data)+4)//5
        if total == 0:
            source.reply(rtr("command.list.nodata"))
            return
        if page < 1 or page > total:
            source.reply(rtr("command.list.page_outofindex"))
            return
        for i in data[(page-1)*5:min(len(data), page*5)]:
            source.reply(Display.show(i["waypoint"], i["id"]))
        pre = rtr("command.list.pre").h(rtr(f"command.list.{'end' if page == 1 else 'pre'}_prompt"))
        if page != 1:
            pre = pre.c(RAction.run_command, f"{self.prefix} list {page-1}")
        next = rtr("command.list.next").h(rtr(f"command.list.{'end' if page == total else 'next'}_prompt"))
        if page != total:
            pre = pre.c(RAction.run_command, f"{self.prefix} list {page+1}")
        source.reply(RTextList(rtr("command.list.left"), pre, rtr("command.list.page", current=page, total=total), next, rtr("command.list.right")))
    

    def search(self, source: CommandSource, context: CommandContext):
        name = context["name"]
        target = self.waypoint_manager.search_name(name)
        if not target:
            source.reply(rtr("command.search.nodata", name=name))
            return
        source.reply(rtr("command.search.title", name=name, count=len(target)))
        for i in target:
            source.reply(Display.show(i["waypoint"], i["id"]))
    

    def info(self, source: CommandSource, context: CommandContext):
        id = context["id"]
        waypoint = self.waypoint_manager.search_id(id)
        if not waypoint:
            source.reply(rtr("command.info.nodata"))
        source.reply(rtr("command.info.show", id=waypoint["id"], creator=waypoint["creator"], create_time=waypoint["create_time"]))
        source.reply(Display.show(waypoint["waypoint"], waypoint["id"]))
    

    @new_thread(f"{PLUGIN_ID}-player_pos")
    def player_pos(self, source: CommandSource, context: CommandContext, player: str):
        player_list = self.api.get_player_list()
        server = source.get_server()
        if player not in player_list:
            server.say(rtr("command.player_pos.nodata"))
        player_pos = self.api.get_player_pos(player)
        if not player_pos:
            return
        waypoint = Waypoint(player_pos["pos"], player_pos["dimension"], player)
        
        server.say(Display.show(waypoint))
        closest = self.waypoint_manager.search_closest(player_pos["pos"], player_pos["dimension"], 128)
        if closest:
            server.say(RTextList(rtr("command.player_pos.closest", distance="%.1f"%closest[1]), Display.show(closest[0]["waypoint"], closest[0]["id"])))


    @new_thread(f"{PLUGIN_ID}-on_user_info")
    def on_user_info(self, server: PluginServerInterface, info: Info):
        waypoint = Waypoint.transform_xaero_waypoint(info.content)
        if waypoint:
            server.reply(info, Display.temporary(waypoint, self.config["command"]["waypoints"]))
            return
        fastsearch = re.match(self.config["command"]["fastsearch_regex"], info.content)
        if not fastsearch:
            return
        name = fastsearch.groups()[0]
        target = self.waypoint_manager.search_name(name)
        if target:
            server.reply(info, rtr("command.search.title", name=name, count=len(target)))
            for i in target:
                server.reply(info, Display.show(i["waypoint"], i["id"]))
            return
        player_list = self.api.get_player_list()
        if not player_list or name not in player_list:
            server.reply(info, rtr("command.fastsearch.nodata", name=name))
            return
        player_pos = self.api.get_player_pos(name)
        if not player_pos:
            server.reply(info, rtr("command.fastsearch.nodata", name=name))
            return
        waypoint = Waypoint(player_pos["pos"], player_pos["dimension"], name)
        server.say(Display.show(waypoint))
        closest = self.waypoint_manager.search_closest(player_pos["pos"], player_pos["dimension"], 64)
        if closest:
            server.say(RTextList(rtr("command.player_pos.closest", distance="%.1f"%closest[1]), Display.show(closest[0]["waypoint"])))



def on_load(server: PluginCommandSource, prev_module):
    global proxy
    proxy = Proxy(server)

def on_user_info(server: PluginServerInterface, info: Info):
    global proxy
    proxy.on_user_info(server, info)

def on_info(server: PluginServerInterface, info: Info):
    proxy.api.on_info(server, info)
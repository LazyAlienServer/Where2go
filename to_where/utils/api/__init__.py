from mcdreforged.api.all import Info, event_listener, ServerInterface
from threading import Event, Union
from typing import TypedDict
import re


class PlayerAPIConfig(TypedDict):
    player_pos_command: str
    player_dimension_command: str
    player_pos_regex: str
    player_dimension_regex: str


class PlayerPos(TypedDict):
    pos: tuple
    dimension: str


class PlayerAPI:

    def __init__(self, config: PlayerAPIConfig) -> None:
        self.player_pos: dict = {}
        self.config = config

    def get_player_pos(self, player: str, timeout: int = 5) -> PlayerPos:
        player_pos = self.player_pos
        if player in player_pos.keys():
            event: Event = player_pos[player]["event"]
        else:
            event = Event()
            event.clear()
            player_pos[player] = {
                "event": event,
                "pos": None,
                "dimension": None
            }
            server = ServerInterface.si()
            server.execute(self.config["player_pos_command"].format(player=player))
            server.execute(self.config["player_dimension_command"].format(player=player))
        event.wait(timeout=timeout)
        pos = player_pos[player]
        player_pos.pop(player)
        return pos

    @event_listener("mcdr.general_info")
    def on_info(self, server, info: Info):
        if not info.is_from_server:
            return
        pos = re.match(self.config.player_pos_regex, info.content) 
        dimension = re.match(self.config.player_dimension_regex, info.content)
        if not pos and not dimension:
            return
        if pos:
            player, pos = pos.groups()
            player_pos = self.player_pos[player]
            if player_pos["pos"]:
                return
            player_pos["pos"] = eval(pos)
            if player_pos["dimension"]:
                player_pos["event"].set()
        elif dimension:
            player, dimension = dimension.groups()
            player_pos = self.player_pos[player]
            if player_pos["dimension"]:
                return
            player_pos["dimension"] = dimension
            if player_pos["pos"]:
                player_pos["event"].set()
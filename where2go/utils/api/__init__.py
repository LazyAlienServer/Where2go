from mcdreforged.api.all import Info, ServerInterface
from threading import Event
from typing import TypedDict, List, Union
import re
from where2go.config import PLAYER_API_CONFIG


class PlayerPos(TypedDict):
    pos: tuple
    dimension: str


class PlayerAPI:

    def __init__(self, config: PLAYER_API_CONFIG) -> None:
        self.player_pos: dict = {}
        self.player_list: dict = {}
        self.config = config

    def get_player_pos(self, player: str, timeout: int = 5) -> Union[None, PlayerPos]:
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
            server.execute(self.config.player_pos_command.format(player=player))
            server.execute(self.config.player_dimension_command.format(player=player))
        event.wait(timeout=timeout)
        pos = player_pos[player]
        player_pos.pop(player)
        return pos if pos["pos"] and pos["event"] else None


    def get_player_list(self, timeout: int = 5) -> Union[List[str], None]:
        if self.player_list:
            event: Event = self.player_list["event"]
        else:
            event = Event()
            self.player_list = {
                "event": event,
                "list": None
            }
            event.clear()
            ServerInterface.si().execute(self.config.player_list_command)
        event.wait(timeout=timeout)
        result = [re.fullmatch(f"{self.config.prefix_regex}(.+)", i).groups()[-1] for i in self.player_list["list"]] if self.player_list["list"] else None
        self.player_list = {}
        return result


    def on_info(self, server, info: Info):
        if not info.is_from_server:
            return
        if self.player_pos:
            pos = re.match(self.config.player_pos_regex.format(prefix_regex = self.config.prefix_regex), info.content) 
            dimension = re.match(self.config.player_dimension_regex.format(prefix_regex = self.config.prefix_regex), info.content)
            if not pos and not dimension:
                return
            if pos:
                player, x, y, z = pos.groups()
                player_pos = self.player_pos[player]
                if player_pos["pos"]:
                    return
                player_pos["pos"] = (int(float(x)), int(float(y)), int(float(z)))
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
        if self.player_list:
            player_list = re.match(self.config.player_list_regex, info.content)
            if player_list:
                self.player_list["list"] = player_list.groups()[-1].split(self.config.player_list_sep)
                self.player_list["event"].set()
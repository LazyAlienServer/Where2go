from mcdreforged.api.all import Info, ServerInterface
from threading import Event
from typing import TypedDict, List, Union, Tuple
import re
from where2go.config import PLAYER_API_CONFIG
from minecraft_data_api import get_player_coordinate, get_player_dimension, get_server_player_list


class PlayerPos(TypedDict):
    pos: Tuple[int, int, int]
    dimension: str

DIM = {
    -1: "the_nether",
    0: "overworld",
    1: "the_end"
}

class PlayerAPI:

    def __init__(self, config: PLAYER_API_CONFIG) -> None:
        self.player_pos: dict = {}
        self.player_list: dict = {}
        self.config = config

    def get_player_pos(self, player: str, timeout: int = 5) -> PlayerPos:
        pos = get_player_coordinate(player)
        dimension = get_player_dimension(player)
        if dimension in DIM.keys():
            dimension = DIM[dimension]
        return {
            "pos": (int(pos.x), int(pos.y), int(pos.z)),
            "dimension": dimension
        }

    def get_player_list(self, timeout: int = 5) -> Union[List[str], None]:
        player_list = [re.fullmatch(f"{self.config.prefix_regex}(.+)", i).groups()[-1] for i in get_server_player_list()[2]]
        return player_list
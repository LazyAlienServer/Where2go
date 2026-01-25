from mcdreforged.api.all import Serializable
from where2go.utils.waypoints.types import ClickEventFormat

class COMMAND_CONFIG(Serializable):
    waypoints: str = "!!wp"
    whereis: str = "!!vris"
    here: str = "!!here"
    fastsearch_regex: str = "^(?P<name>\w+)在哪里?？?$"
    fastsearch_prompt: str = "XXX在哪"
    page_size: int = 5

class PLAYER_API_CONFIG(Serializable):
    prefix_regex: str = "(?:\[.+\])?"
    player_list_sep: str = ", "
    highlight_command: str = "effect give {player} minecraft:glowing 15 0 true"

class XAERO_CONFIG(Serializable):
    click_event_format: ClickEventFormat = ["old", "new"]

class CONFIG(Serializable):
    xaero: XAERO_CONFIG = XAERO_CONFIG()
    command: COMMAND_CONFIG = COMMAND_CONFIG()
    player_api: PLAYER_API_CONFIG = PLAYER_API_CONFIG()
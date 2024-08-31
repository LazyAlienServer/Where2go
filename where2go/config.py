from mcdreforged.api.all import Serializable

class COMMAND_CONFIG(Serializable):
    waypoints: str = "!!wp"
    whereis: str = "!!vris"
    here: str = "!!here"
    fastsearch_regex: str = "^(\w+)在哪？?"
    fastsearch_prompt: str = "XXX在哪"

class PLAYER_API_CONFIG(Serializable):
    prefix_regex: str = "(?:\[.+\])?"
    player_pos_command: str = "data get entity {player} Pos"
    player_dimension_command: str = "data get entity {player} Dimension"
    player_pos_regex: str = "^{prefix_regex}(\w+) has the following entity data: \[(-?[0-9.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]"
    player_dimension_regex: str = '^{prefix_regex}(\w+) has the following entity data: "minecraft:(\w+)"'
    player_notfound_regex: str = '^No entity was found'
    player_list_command: str = "list"
    player_list_sep: str = ", "
    player_list_regex: str = '^There are [0-9]+ of a max of [0-9]+ players online: (.+)*'
    highlight_command: str = "effect give {player} minecraft:glowing 15 0 true"

class CONFIG(Serializable):
    command: COMMAND_CONFIG = COMMAND_CONFIG()
    player_api: PLAYER_API_CONFIG = PLAYER_API_CONFIG()
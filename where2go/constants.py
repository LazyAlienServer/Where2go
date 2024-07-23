DEFAULT_CONFIG = {
    "command": {
        "waypoints": "!!wp",
        "whereis": "!!vris",
        "here": "!!here",
        "fastsearch_regex": "^(\w+)在哪？?",
        "fastsearch_prompt": "XXX在哪"
    },
    "player_api": {
        "prefix_regex": "(?:\[.+\])?",
        "player_pos_command": "data get entity {player} Pos",
        "player_dimension_command": "data get entity {player} Dimension",
        "player_pos_regex": "^{prefix_regex}(\w+) has the following entity data: \[(-?[0-9.]+)d, (-?[0-9.]+)d, (-?[0-9.]+)d\]",
        "player_dimension_regex": '^{prefix_regex}(\w+) has the following entity data: "minecraft:(\w+)"',
        "player_notfound_regex": '^No entity was found',
        "player_list_command": "list",
        "player_list_sep": ", ",
        "player_list_regex": '^There are [0-9]+ of a max of [0-9]+ players online: (.+)*'
    }
}

PLUGIN_ID = "where2go"
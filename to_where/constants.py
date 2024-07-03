DEFAULT_CONFIG = {
    "command": {
        "waypoints": "!!wp",
        "whereis": "!!vris",
        "here": "!!here"
    },
    "waypoint": {
        "dimension": {
            "xaero": {
                "Internal-overworld-waypoints":0,
                "Internal-the-nether-waypoints":1,
                "Internal-the-end-waypoints":2
            }
        }
    },
    "display": {
        "dimension": {
            0: "§2主世界 §a[{x}, {y}, {z}]§f",
            1: "§c地狱 §4[{x}, {y}, {z}]§f",
            2: "§d末地 §5[{x}, {y}, {z}]§f"
        }
    },
    "player_api": {
        "player_pos_command": "data get entity {player} Pos",
        "player_dimension_command": "data get entity {plater} Dimension",
        "player_pos_regex": "^(?:\[.+\])?(\w{3,16}) has the following entity data: \[(-?[0-9.]+d, -?[0-9.]+d, -?[0-9.]+d)\]",
        "player_dimension_regex": '^(?:\[.+\])?(\w{3,16}) has the following entity data: "minecraft:(\w+)"',
        "player_notfound_regex": '^No entity was found',
        "player_list_command": "list",
        "player_list_regex": '^There are [0-9]+ of a max of [0-9]+ players online: (.+)*'
    }
}
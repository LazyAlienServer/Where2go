from .waypoint import Waypoint

class Display:

    def __init__(self, config: dict) -> None:
        self.config = config

    def show(self, waypoint: Waypoint):
        x, y, z = waypoint.pos
        msg = [
            {"text":"§e@§f §l%s§r"%waypoint["name"]},
            {"text":" §7-§f"},
            {"text":(f'f"%s"'%self.config["dimension"][waypoint.dimension])},
            {"text":" "},
            {"text":"[+X]",
             "color":"gold",
             "clickEvent":{"action":"run_command", "value":"xaero_waypoint_add:%s"%waypoint.get_xaero_waypoint()},
             "hoverEvent":{"action":"show_text", "value":{"text":"添加Xaero坐标点", "color":"gold"}}},
            {"text":" "}
        ]
        return msg
    
    def waypoint_error(self):
        return {"text":"§c错误的坐标点"}
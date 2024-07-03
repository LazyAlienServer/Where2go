from .waypoint import Waypoint
from .display import Display
from mcdreforged.api.all import PluginServerInterface
from typing import TypedDict, List
import time, datetime, difflib


class WaypointData(TypedDict):
    id: str
    create_time: str
    creator: str
    waypoint: Waypoint


class WaypointManager:

    def __init__(self, save_everytime = True) -> None:
        self.server: PluginServerInterface = PluginServerInterface.get_instance()
        self.data = self.server.load_config_simple("waypoints_data.json", default_config=[])
        self.data: List[WaypointData] = self._load_data
        self.save_everytime = save_everytime
    

    def _load_data(self):
        for i in self.data:
            i["waypoint"] = Waypoint(**i["waypoint"])
    

    def _save_data(self):
        data = self.data.copy()
        for i in data:
            i["waypoint"] = i["waypoint"].to_dict()
        self.server.save_config_simple(data, "waypoints_data.json")
    

    def _gen_id(self) -> str:
        int_string = int(time.time()*100)
        id_map = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        id = ""
        length = len(id_map)
        while int_string > length:
            id = id_map[int_string%length] + id
            int_string = int_string//length
        id = id_map[int_string] + id
        return id


    def add(self, creator: str, waypoint: Waypoint) -> WaypointData:
        data = {
            "id": self._gen_id(),
            "create_time": datetime.datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"),
            "creator": creator,
            "waypoint": waypoint
        }
        self.data.append(data)
        if self.save_everytime:
            self._save_data()
        return data

    
    def remove(self, id: str) -> False | WaypointData:
        data = self.search_id(id)
        if not data:
            return False
        self.data.remove(data)
        if self.save_everytime:
            self._save_data()
        return data
    

    def save(self):
        self._save_data()
    

    def search_name(self, content: str) -> List[WaypointData]:
        targets = [data for data in self.data if self.is_string_similar(data["waypoint"].name, content)]
        return targets
    

    def search_distance(self, pos: tuple, distance: int) -> List[WaypointData]:
        targets = [data for data in self.data if data["waypoint"].is_close_to(pos, distance)]
        return targets
    

    def search_id(self, id: str) -> None | WaypointData:
        id_list = [data["id"] for data in self.data]
        if id not in id_list:
            return None
        data = self.data[id_list.index(id)]
        return data

    
    def is_string_similar(self, string1, string2, similarity = 0.5):
        return difflib.SequenceMatcher(None,string1,string2).quick_ratio() >= similarity
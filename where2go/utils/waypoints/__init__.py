from .waypoint import Waypoint
from .display import Display
from mcdreforged.api.all import PluginServerInterface
from typing import TypedDict, List, Union, Tuple
import time, datetime, difflib, os, json
from where2go.constants import PLUGIN_ID
from copy import deepcopy


class WaypointData(TypedDict):
    id: str
    create_time: str
    creator: str
    waypoint: Waypoint


class WaypointManager:

    def __init__(self, server: PluginServerInterface, save_everytime = True) -> None:
        self.server = server
        path = server.get_data_folder()
        if not os.path.isdir(path):
            os.makedirs(path)
        self.file = os.path.join(path, "data.json")
        with open(self.file, "r+" if os.path.isfile(self.file) else "w+") as file:
            data = file.read()
            try:
                data = json.loads(data)
            except:
                data = []
                file.write("[]")
            file.close()
        self.data: List[WaypointData] = data
        self._load_data()
        self.save_everytime = save_everytime
    

    def _load_data(self):
        for i in self.data:
            i["waypoint"] = Waypoint(**i["waypoint"])
    

    def _save_data(self):
        data = deepcopy(self.data)
        for i in data:
            i["waypoint"] = i["waypoint"].to_dict()
        with open(self.file, "w") as file:
            file.write(json.dumps(data, indent="    "))
            file.close()
    

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

    
    def remove(self, id: str) -> Union[False, WaypointData]:
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
    

    def search_distance(self, pos: tuple, dimension, distance: int) -> List[WaypointData]:
        targets = [data for data in self.data if data["waypoint"].dimension == dimension and data["waypoint"].is_close_to(pos, distance)]
        return targets
    

    def search_id(self, id: str) -> Union[None, WaypointData]:
        id_list = [data["id"] for data in self.data]
        if id not in id_list:
            return None
        data = self.data[id_list.index(id)]
        return data
    

    def search_closest(self, pos: tuple, dimension, max_distance: int = None) -> Union[None, Tuple[WaypointData, int]]:
        targets = [data["waypoint"].distance(pos) for data in self.data if data["waypoint"].dimension == dimension]
        min_distance = min(targets)
        return (self.data[targets.index(min_distance)], min_distance) if max_distance == None or min_distance <= max_distance else None

    
    def is_string_similar(self, string1, string2, similarity = 0.5):
        return difflib.SequenceMatcher(None,string1,string2).quick_ratio() >= similarity
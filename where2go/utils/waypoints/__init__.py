from .waypoint import Waypoint
from mcdreforged.api.all import PluginServerInterface
from typing import List, Union, Tuple, Optional, Literal, Dict
import time, datetime, difflib, os, json
from copy import deepcopy
from where2go.utils.waypoints.types import WaypointData
from where2go.utils.waypoints.rtext_utils import RTextWaypoint, RTextWaypointSimple, RTextWaypointError


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

    
    def remove(self, id: str) -> Union[None, WaypointData]:
        data = self.search_id(id)
        if not data:
            return None
        self.data.remove(data)
        if data.get("link", None):
            linked_data = self.search_id(data["link"])
            if linked_data:
                del linked_data["link"]
        if self.save_everytime:
            self._save_data()
        return data
    

    def link(self, id1: str, id2: str) -> Union[None, Tuple[WaypointData, WaypointData], Tuple[str, str]]:
        index1 = self.search_index(id1)
        index2 = self.search_index(id2)
        if index1 is None or index2 is None:
            return None
        if (link1 := self.data[index1].get("link", None)) or (link2 := self.data[index2].get("link", None)):
            return (link1, link2 if not link1 else self.data[index2].get("link", None))
        self.data[index1]["link"] = id2
        self.data[index2]["link"] = id1
        if self.save_everytime:
            self._save_data()
        return (self.data[index1], self.data[index2])
    

    def unlink(self, id: str) -> Union[None, Literal[False], Tuple[WaypointData, Optional[WaypointData]]]:
        index = self.search_index(id)
        if index is None:
            return None
        linked_id = self.data[index].get("link", None)
        if linked_id is None:
            return False
        linked_index = self.search_index(linked_id)
        if linked_index is None:
            del self.data[index]["link"]
            if self.save_everytime:
                self._save_data()
            return (self.data[index], None)
        del self.data[index]["link"]
        del self.data[linked_index]["link"]
        if self.save_everytime:
            self._save_data()
        return (self.data[index], self.data[linked_index])
    

    def save(self):
        self._save_data()
    

    def filter_linked_waypoints(self, datas: List[WaypointData]) -> List[WaypointData]:
        filtered_datas = []
        linked_ids = set()
        for data in datas:
            if data["id"] in linked_ids:
                continue
            if linked_id := data.get("link", None):
                linked_ids.add(linked_id)
                if (linked_waypoint := self.search_id(linked_id))["waypoint"].dimension == "overworld":
                    filtered_datas.append(linked_waypoint)
                    continue
            filtered_datas.append(data)
        return filtered_datas



    def search_name(self, content: str) -> List[WaypointData]:
        targets = [data for data in self.data if self.is_string_similar(data["waypoint"].name, content) or content in data["waypoint"].name]
        return self.filter_linked_waypoints(targets)
    

    def search_distance(self, pos: tuple, dimension, distance: int) -> List[WaypointData]:
        targets = [data for data in self.data if data["waypoint"].dimension == dimension and data["waypoint"].is_close_to(pos, distance)]
        return self.filter_linked_waypoints(targets)
    

    def search_index(self, id: str, default = None) -> Optional[int]:
        id_list = [data["id"] for data in self.data]
        if id not in id_list:
            return default
        return id_list.index(id)


    def search_id(self, id: str, default = None) -> Optional[WaypointData]:
        id_list = [data["id"] for data in self.data]
        if id not in id_list:
            return default
        data = self.data[id_list.index(id)]
        return data
    

    def search_closest(self, pos: tuple, dimension, max_distance: int = None) -> Union[None, Tuple[WaypointData, int]]:
        targets = [data for data in self.data if data["waypoint"].dimension == dimension]
        distance = [i["waypoint"].distance(pos) for i in targets]
        if not distance:
            return
        min_distance = min(distance)
        return (targets[distance.index(min_distance)], min_distance) if max_distance is None or min_distance <= max_distance else None
    
    
    def search_portal_candidates(self) -> Dict[str, List[WaypointData]]:
        candidates = {}
        for i, data1 in enumerate(self.data):
            if data1.get("link", None):
                continue
            waypoint1 = data1["waypoint"]
            candidates[data1["id"]] = []
            for j, data2 in enumerate(self.data):
                if i >= j:
                    continue
                waypoint2 = data2["waypoint"]
                if self.is_nether_portal(waypoint1, waypoint2):
                    candidates[data1["id"]].append(data2)
        return candidates
    

    def get_linked_waypoint_data(self, waypoint_data: WaypointData, default = None) -> Optional[WaypointData]:
        return self.search_id(waypoint_data["link"]) if waypoint_data.get("link", None) else default


    def is_nether_portal(self, waypoint: Waypoint, target_waypoint: Waypoint) -> bool:
        if {waypoint.dimension, target_waypoint.dimension} != {"overworld", "the_nether"}:
            return False
        if waypoint.dimension == "overworld":
            overworld_pos = waypoint.pos
            nether_pos = target_waypoint.pos
        else:
            overworld_pos = target_waypoint.pos
            nether_pos = waypoint.pos
        return abs(overworld_pos[0]//8 - nether_pos[0]) <= 16 and abs(overworld_pos[2]//8 - nether_pos[2]) <= 16

    
    def is_string_similar(self, string1, string2, similarity = 0.5):
        return difflib.SequenceMatcher(None,string1,string2).quick_ratio() >= similarity
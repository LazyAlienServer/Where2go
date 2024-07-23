from mcdreforged.api.all import ServerInterface
from where2go.constants import PLUGIN_ID
from mcdreforged.api.all import RTextList, RText, RAction


def rtr(key, *args, **kwargs):
    return ServerInterface.si().rtr(PLUGIN_ID+"."+key, *args, **kwargs)

help_dict = {
    "add": "<waypoint>",
    "remove": "<id>",
    "list": "[page]",
    "search": "<name>",
    "info": "<id>",
}

def help_msg(key, prefix):
    return RTextList(RText(f"§7{prefix} {key} {help_dict[key]}").c(RAction.run_command, f"{prefix} {key}"), " ", rtr(f"help.{key}"))
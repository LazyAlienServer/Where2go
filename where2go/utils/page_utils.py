from typing import List, Any, Union
from enum import Enum
import re
from mcdreforged.api.all import CommandContext
from where2go.utils.display_utils import rtr
from mcdreforged.api.all import RTextList, RAction, RTextMCDRTranslation

class PageValidationError(Enum):
    INVALID = "page_error"
    OUT_OF_INDEX = "page_outofindex"
    NO_DATA = "nodata"

class Page:

    def __init__(self, items: List[Any], page_size: int, command: str) -> None:
        '''Initialize a pagination object.

Parameters
----
items : List[Any]
  The list of items to paginate.

page_size : int
  Number of items per page.

prefix : str
  The command prefix for navigation commands.'''
        if page_size <= 0:
            raise ValueError("page_size must be greater than 0")
        self.items = items
        self.page_size = page_size
        self.total_pages: int = (len(items) + page_size - 1) // page_size
        self.current_page: Union[PageValidationError, int] = PageValidationError.NO_DATA if self.total_pages == 0 else 1
        self.command = command

    def set_page_index(self, context: CommandContext) -> bool:
        '''Get the page number from the command context.

Parameters
----
context : CommandContext
  including "page" key optionally.

Returns
----
bool
  True if the page number is valid, False otherwise.'''
        if "page" not in context.keys():
            if self.total_pages == 0:
                return False
            self.current_page = 1
            return True
        page_str = context["page"]
        if not re.fullmatch("[0-9]+", page_str):
            self.current_page = PageValidationError.INVALID
            return False
        page_int = int(page_str)
        if page_int < 1 or page_int > self.total_pages:
            self.current_page = PageValidationError.OUT_OF_INDEX
            return False
        self.current_page = int(page_str)
        return True

    def get_items_on_page(self) -> List[Any]:
        if isinstance(self.current_page, PageValidationError):
            return []
        start_index = (self.current_page - 1) * self.page_size
        end_index = start_index + self.page_size

        return self.items[start_index:end_index]
    
    def get_rtext(self) -> Union[RTextList, RTextMCDRTranslation]:
        page = self.current_page
        if isinstance(page, PageValidationError):
            return rtr(f"page.{page.value}")
        total = self.total_pages
        pre = rtr("page.pre").h(rtr(f"page.{'end' if page == 1 else 'pre'}_prompt"))
        if page != 1:
            pre = pre.c(RAction.run_command, f"{self.command} {page-1}")
        next = rtr("page.next").h(rtr(f"page.{'end' if page == total else 'next'}_prompt"))
        if page != total:
            next = next.c(RAction.run_command, f"{self.command} {page+1}")
        return RTextList(rtr("page.left"), pre, rtr("page.page", current=page, total=total), next, rtr("page.right"))
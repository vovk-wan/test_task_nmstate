"""
views.py
---------
The module contains all the views used in the application.
"""

import curses

from abc import ABC, abstractmethod

from widgets import TextEdit, Checkbox, RadioGroupState, Button


MAPPER_WIDGET = {
    "text": TextEdit,
    "bool": Checkbox,
    "state_bool": RadioGroupState,
    "ipv4address": TextEdit,
    "bridge_name": TextEdit,
    "apply_button": Button,
}


class View(ABC):
    """The base class for all views."""

    def __init__(self, parent: curses.window, items: list):
        self.parent = parent
        height, width = self.parent.getmaxyx()
        begin_y, begin_x = self.parent.getbegyx()
        border_top = 2
        border_left = 2
        window_height = height - border_top * 2
        window_width = width - border_left * 2
        window_top = begin_y + border_top
        window_left = begin_x + border_left
        self.window_width = window_width
        self.window = self.parent.subwin(
            window_height, window_width, window_top, window_left
        )

        self.parent.box()

        self.window.keypad(True)

        self.position = 0
        self.items = items

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    @abstractmethod
    def show(self):
        pass


class MenuView(View):
    """The menu presentation class is used to select an Ethernet interface and open it for modification."""

    def __init__(self, parent: curses.window, items: list[dict]):
        super().__init__(parent, items)
        self.parent.addstr(0, 0, "Menu")

    def show(self) -> None:
        """Menu drawing method."""
        self.window.clear()
        self.parent.refresh()
        self.window.refresh()
        curses.doupdate()
        for i, item in enumerate(self.items):
            if i == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            caption = f"{i}. {item.name}"
            self.window.addstr(1 + i, 1, caption, mode)


class InterfaceView(View):
    """The interface presentation class is used to modify the Ethernet interface."""

    def __init__(self, parent: curses.window, items: list, interface):
        super().__init__(parent, items)
        self.interface = interface
        self.parent.addstr(0, 0, "Interface")
        self.parent.hline(1, 1, " ", self.window_width - 2)
        self.parent.addstr(1, 1, f"name: {interface.name}, type: {interface.type}")
        self.full_items = items

    def show(self):
        """Menu drawing method."""

        self.window.clear()
        self.parent.refresh()
        self.window.refresh()
        curses.doupdate()
        self.add_widgets()

    def add_widgets(self):
        """The method adds widgets to the interfaceview window."""

        border_top = 2
        border_left = 2
        self.set_show_items()
        for i, item in enumerate(self.items):
            if i == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL
            widget = MAPPER_WIDGET[item["type"]]
            editor = widget(self.window, border_top, border_left, i, item["name"], mode)
            editor.value = item["value"]
            item["editor"] = editor
            editor.show()

    def set_show_items(self):
        """The method sets the elements available for display."""

        res = {item["name"]: item["value"] for item in self.full_items}
        show_items = []
        if res["state"] == "down":
            show_items = ["state", "apply"]
        elif res["bridge"]:
            show_items = ["bridge", "bridge name", "apply"]
        elif res["ipv4 dhcp"]:
            show_items = ["state", "ipv4 dhcp", "bridge", "apply"]
        elif not res["ipv4 dhcp"]:
            show_items = ["state", "ipv4 dhcp", "ipv4 address", "bridge", "apply"]

        self.items = [item for item in self.full_items if item["name"] in show_items]

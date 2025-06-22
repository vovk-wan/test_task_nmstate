"""
controllers.py
--------------
The module contains controllers for working with the Curses library.
"""

import curses

from typing import Callable

from views import MenuView, InterfaceView
from models import NetInterface
from validators import get_validator
from consts import Color


def get_editor_controller(type: str) -> Callable:
    """
    Function returns a controller for the editor.

    Args:
        type: type of field to select controller

    Returns: the  controller function for the editor
    """

    if type in ("text", "bridge_name", "ipv4address"):
        return texteditor_controller
    elif type == "bool":
        return checkbox_controller
    elif type == "state_bool":
        return radiogroup_controller
    elif type == "apply_button":
        return apply_button_controller


def texteditor_controller(item: dict) -> None:
    """
    The function handles pressing keyboard keys in the TextEdit widget.

    Args:
        item: description of the field and widget for the interface
    """

    editor = item["editor"]
    editor.color = curses.color_pair(Color.EDITOR_COLOR)
    curses.curs_set(1)
    while True:
        editor.show()
        key = editor.window.getch()
        if key == 27:
            break
        if key in [curses.KEY_ENTER, ord("\n")]:

            if get_validator(item["type"])(editor.value):
                editor.color = curses.A_NORMAL
                item["value"] = editor.value
                break
            editor.color = curses.color_pair(Color.ERROR_VALIDATION_COLOR)
            editor.window.refresh()
        else:
            editor.handle_input(key)
    curses.curs_set(0)


def checkbox_controller(item: dict) -> None:
    """
    The function handles pressing enter keys in the CheckBox widget.

    Args:
        item: description of the field and widget for the interface
    """

    editor = item["editor"]
    editor.toggle()
    item["value"] = editor.value


def apply_button_controller(*args) -> str:
    """
    The function handles pressing enter keys in the apply button widget.

    Args:
        args: any positional arguments parameter for compatibility
    """

    return "apply"


def radiogroup_controller(item: dict) -> None:
    """
    The function handles pressing keys in the Radiogroup widget.

    Args:
        item: description of the field and widget for the interface
    """

    editor = item["editor"]
    while True:
        editor.color = curses.A_REVERSE
        editor.show()
        key = editor.window.getch()
        if key == 27:
            break
        if key in [curses.KEY_ENTER, ord("\n")]:
            item["value"] = editor.value
            editor.color = curses.A_NORMAL
            break
        else:
            editor.handle_input(key)


def interface_controller(interface: NetInterface, stdscr: curses.window, y: int, x: int) -> None | str:
    """
    The function handles pressing keys in the InterfaceView.

    Args:
        interface: ethernet interface
        stdscr: main application window
        y: indent from top edge
        x: indent from left edge

    Returns: str or None
    """

    height, weight = stdscr.getmaxyx()
    interfaces_height = height - y
    interfaces_width = 35
    interfaces_top = y
    interfaces_left = x
    interfaces_win = stdscr.subwin(interfaces_height, interfaces_width, interfaces_top, interfaces_left)
    interface_view = InterfaceView(interfaces_win, interface.serialize(), interface)
    item = None
    while True:
        interface_view.parent.bkgd(" ", curses.color_pair(Color.ACTIVE_COLOR))
        interface_view.show(item)
        item = None

        key = interface_view.window.getch()

        if key == 27:
            interface_view.parent.bkgd(" ", curses.color_pair(Color.INACTIVE_COLOR))
            interface_view.parent.refresh()
            stdscr.hline(1, 2, " ", weight - 2)
            stdscr.refresh()
            break
        elif key in [curses.KEY_ENTER, ord("\n")]:
            stdscr.hline(1, 2, " ", weight - 2)
            stdscr.refresh()
            item = interface_view.items[interface_view.position]
            editor = get_editor_controller(item["type"])
            result = editor(item)
            if result == "apply":
                errors = []
                for validate_item in interface_view.items:
                    editor = validate_item["editor"]
                    if not get_validator(validate_item["type"])(editor.value):
                        errors.append(validate_item["name"])
                if errors:
                    stdscr.addstr(
                        1, 2, f"errors field - {', '.join(errors)}", curses.color_pair(Color.ERROR_VALIDATION_COLOR)
                    )
                    stdscr.refresh()
                else:
                    res = interface_view.interface.apply(
                        **{item["name"]: item["value"] for item in interface_view.items}
                    )
                    stdscr.addstr(1, 2, res)
                    stdscr.refresh()
                    if res.lower() == "ok":
                        interface_view.parent.clear()
                        interface_view.parent.refresh()
                        return "reload"
        elif key == curses.KEY_UP:
            interface_view.navigate(-1)
        elif key == curses.KEY_DOWN:
            interface_view.navigate(1)
        elif key == ord("q"):
            return "exit"


def menu_controller(stdscr: curses.window, y: int, x: int) -> None:
    """
    The function handles pressing keys in the MenuView.

    Args:
        stdscr: main application window
        y: indent from top edge
        x: indent from left edge
    """

    height, width = stdscr.getmaxyx()

    menu_height = height - y
    menu_width = 35
    menu_top = y
    menu_left = x

    menu_win = stdscr.subwin(menu_height, menu_width, menu_top, menu_left)

    NetInterface.update_interfaces()

    menu = MenuView(menu_win, NetInterface.ethernet_interfaces)
    while True:
        menu.parent.bkgd(" ", curses.color_pair(Color.ACTIVE_COLOR))
        menu.window.bkgd(" ", curses.color_pair(Color.ACTIVE_COLOR))
        menu.show()
        key = menu.window.getch()

        if key in [curses.KEY_ENTER, ord("\n")]:
            menu.parent.bkgd(" ", curses.color_pair(Color.INACTIVE_COLOR))
            menu.window.bkgd(" ", curses.color_pair(Color.INACTIVE_COLOR))
            menu.parent.refresh()
            res = interface_controller(
                menu.items[menu.position], stdscr, y, x + x + menu_width
            )
            if res == "reload":
                NetInterface.update_interfaces()
                menu = MenuView(menu_win, NetInterface.ethernet_interfaces)
            elif res == "exit":
                break
        elif key == curses.KEY_UP:
            menu.navigate(-1)
        elif key == curses.KEY_DOWN:
            menu.navigate(1)
        elif key == ord("q"):
            break

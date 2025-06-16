import curses
from typing import Callable

from views import MenuView, InterfaceView
from models import NetInterface
from validators import get_validator
from consts import Color


def get_editor_controller(item: dict) -> Callable:
    """
    Function returns a controller for the editor.
    Args:
        item: dict

    Returns: Callable
    """

    if item["type"] in ("text", "bridge_name", "ipv4address"):
        return texteditor_controller
    elif item["type"] == "bool":
        return checkbox_controller
    elif item["type"] == "state_bool":
        return radiogroup_controller
    elif item["type"] == "apply_button":
        return apply_button_controller


def texteditor_controller(item) -> None:
    editor = item["editor"]
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


def ipv4editor_controller(item):
    editor = item["editor"]
    curses.curs_set(1)
    while True:
        editor.show()
        key = editor.window.getch()
        if key == 27:
            break
        if key in [curses.KEY_ENTER, ord("\n")]:
            item["value"] = list(editor.value)
            break
        else:
            editor.handle_input(key)
    curses.curs_set(0)


def checkbox_controller(item):
    editor = item["editor"]
    editor.toggle()
    item["value"] = editor.is_checked()


def apply_button_controller(item):
    return "apply"


def radiogroup_controller(item):
    editor = item["editor"]
    while True:
        editor.show()
        key = editor.window.getch()
        if key == 27:
            break
        if key in [curses.KEY_ENTER, ord("\n")]:
            item["value"] = editor.value
            break
        else:
            editor.handle_input(key)


def interface_controller(
    interface: NetInterface, stdscr: curses.window, y: int, x: int
):

    height, weight = stdscr.getmaxyx()
    interfaces_height = height - y
    interfaces_width = 35
    interfaces_top = y
    interfaces_left = x
    interfaces_win = stdscr.subwin(
        interfaces_height, interfaces_width, interfaces_top, interfaces_left
    )
    interface_view = InterfaceView(interfaces_win, interface.serialize(), interface)
    while True:
        interface_view.parent.bkgd(" ", curses.color_pair(Color.ACTIVE_COLOR))
        interface_view.show()

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
            editor = get_editor_controller(interface_view.items[interface_view.position])
            result = editor(interface_view.items[interface_view.position])
            if result == "apply":
                errors = []
                for item in interface_view.items:
                    editor = item["editor"]
                    if not get_validator(item["type"])(editor.value):
                        errors.append(item["name"])
                if errors:
                    stdscr.addstr(
                        1, 2, f"errors field - {', '.join(errors)}", curses.A_BLINK
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


def menu_controller(stdscr, y, x):
    height, width = stdscr.getmaxyx()

    menu_height = height - y
    menu_width = 35
    menu_top = y
    menu_left = x

    menu_win = stdscr.subwin(menu_height, menu_width, menu_top, menu_left)

    NetInterface.update_interfaces()
    menu_items = [iface for iface in NetInterface.ethernet_interfaces]

    menu = MenuView(menu_win, menu_items)
    while True:
        menu.parent.bkgd(" ", curses.color_pair(Color.ACTIVE_COLOR))
        menu.parent.refresh()
        menu.show()
        key = menu.window.getch()

        if key in [curses.KEY_ENTER, ord("\n")]:
            menu.parent.bkgd(" ", curses.color_pair(Color.INACTIVE_COLOR))
            menu.parent.refresh()
            res = interface_controller(
                menu.items[menu.position], stdscr, y, x + x + menu_width
            )
            if res == "reload":
                NetInterface.update_interfaces(force=True)
                menu_items = [iface for iface in NetInterface.ethernet_interfaces]

                menu = MenuView(menu_win, menu_items)
        elif key == ord("q"):
            break
        elif key == curses.KEY_UP:
            menu.navigate(-1)
        elif key == curses.KEY_DOWN:
            menu.navigate(1)

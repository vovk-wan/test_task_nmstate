"""
app.py
---------
Module for initializing the application and assigning initial parameters to curses
"""

import curses
import subprocess

from controllers import menu_controller
from consts import Color


class MyApp:
    """Entry point class and initialization of initial values for the application."""

    def __init__(self, stdscr):
        self.screen = stdscr
        curses.start_color()

        curses.init_pair(Color.WINDOW_COLOR, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(Color.ACTIVE_COLOR, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(Color.INACTIVE_COLOR, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(Color.ACTIVE_BUTTON_COLOR, curses.COLOR_YELLOW, curses.COLOR_BLUE)
        curses.init_pair(Color.INACTIVE_BUTTON_COLOR, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(Color.ERROR_VALIDATION_COLOR, curses.COLOR_RED, curses.COLOR_WHITE)

        curses.init_pair(Color.EDITOR_COLOR, curses.COLOR_WHITE, curses.COLOR_BLUE)

        stdscr.bkgd(" ", curses.color_pair(Color.WINDOW_COLOR))

        stdscr.addstr(0, 1, f"ESC - cancel, arrows - navigation, Enter - edit/save, q - exit")
        stdscr.refresh()
        curses.curs_set(0)

        border_top = 2
        border_left = 2

        menu_controller(stdscr, border_top, border_left)


if __name__ == "__main__":
    curses.wrapper(MyApp)

    if b"linux" == curses.termname():
        subprocess.run(["reset"])

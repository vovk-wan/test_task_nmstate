"""
widgets.py
------------
The module contains widgets for working with fields
"""


import curses

from abc import ABC, abstractmethod

from consts import Color


class Widget(ABC):
    """The base class for widgets"""

    def __init__(
            self, parent: curses.window,
            border_top: int,
            border_left: int,
            index: int,
            caption: str,
            mode: curses.color_pair
    ):
        """
        The initialization of the text edit widget.
        Args:
            parent: parent window
            border_top: size of top border to parent window
            border_left: size of left border to parent window
            index: index of the element in the parent window
            caption: caption of the text edit widget
            mode: color display mode
        """

        self.parent = parent
        begin_y, begin_x = self.parent.getbegyx()
        y = begin_y + border_top + index + border_top * index
        x = begin_x + border_left
        self.border_top = border_top
        self.border_left = border_left
        self.width = 21
        self.window = self.parent.subwin(3, self.width, y, x)
        self.window.box()
        self.window.addstr(0, 0, caption, mode)
        self.color = curses.color_pair(Color.WINDOW_COLOR)
        self.y = 1
        self.x = 1

    @abstractmethod
    def show(self):
        pass


class TextEdit(Widget):
    """The class represents a text edit widget."""

    def __init__(
            self, parent, border_top, border_left, index, caption, mode):
        super().__init__(parent, border_top, border_left, index, caption, mode)
        height, width = self.window.getmaxyx()
        self.width = width - 2 - 1
        self.cursor_pos = 0
        self.window.keypad(True)
        self.value = ""

    def show(self) -> None:
        """Widget drawing method."""

        self.window.hline(self.y, self.x, " ", self.width)
        display_text = self.value[: self.width]
        self.window.bkgd(" ", self.color)
        self.window.addstr(self.y, self.x, display_text)
        cursor_x = self.x + self.cursor_pos
        self.window.move(self.y, cursor_x)
        self.window.refresh()

    def handle_input(self, key: int) -> None:
        """
        Handle keypress.

        Args:
            key: ascii key code
        """

        self.color = curses.color_pair(Color.EDITOR_COLOR)
        if key == curses.KEY_LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
        elif key == curses.KEY_RIGHT:
            if self.cursor_pos < len(self.value):
                self.cursor_pos += 1
        elif key == curses.KEY_BACKSPACE:
            if self.cursor_pos > 0:
                self.value = (
                    self.value[: self.cursor_pos - 1] + self.value[self.cursor_pos:]
                )
                self.cursor_pos -= 1
        elif key == curses.KEY_DC:
            if self.cursor_pos > 0:
                self.value = (
                    self.value[: self.cursor_pos] + self.value[self.cursor_pos + 1:]
                )
        elif 32 <= key < 127:
            if len(self.value) < self.width:
                self.value = (
                    self.value[: self.cursor_pos]
                    + chr(key)
                    + self.value[self.cursor_pos:]
                )
                self.cursor_pos += 1


class Checkbox(Widget):
    def __init__(self, parent, border_top, border_left, index, caption, mode):
        super().__init__(parent, border_top, border_left, index, caption, mode)
        self.value = False

    def show(self):
        """Widget drawing method."""

        checkbox_str = " [X] ON " if self.value else " [ ] OFF"
        self.window.addstr(self.y, self.x, checkbox_str)
        self.window.refresh()

    def toggle(self):
        """Switching Method Value."""
        self.value = not self.value


class RadioGroupState(Widget):
    def __init__(self, parent, border_top, border_left, index, caption, mode):
        super().__init__(parent, border_top, border_left, index, caption, mode)
        self.options = ["UP", "DOWN"]
        self.selected_index = 0
        self.spacing = 3
        self.window.keypad(True)

    @property
    def value(self):
        return self.options[self.selected_index].lower()

    @value.setter
    def value(self, value):
        self.selected_index = self.options.index(value.upper())

    def show(self):
        """Widget drawing method."""

        current_x = self.x
        for idx, option in enumerate(self.options):
            if idx == self.selected_index:
                prefix = " (*)"
                line = f"{prefix} {option}"
                mode = self.color
            else:
                prefix = " ( )"
                line = f"{prefix} {option}"
                mode = curses.A_NORMAL

            self.window.addstr(self.y, current_x, line, mode)

            current_x += len(line) + self.spacing
        self.window.refresh()

    def handle_input(self, key):
        """
        Handle keypress.

        Args:
            key: ascii key code
        """
        if key == curses.KEY_LEFT:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == curses.KEY_RIGHT:
            self.selected_index = min(len(self.options) - 1, self.selected_index + 1)


class Button(Widget):
    def __init__(self, parent, border_top, border_left, index, caption, mode):
        super().__init__(parent, border_top, border_left, index, caption, mode)
        height, width = self.window.getmaxyx()
        self.y = 1
        self.caption = caption
        self.x = (width - len(caption)) // 2
        self.value = lambda: None
        self.mode = mode
        self.window.box()
        self.window.addstr(self.y, self.x, self.caption)

    def show(self):
        """Widget drawing method."""

        if self.mode == curses.A_NORMAL:
            self.window.bkgd(" ", curses.color_pair(Color.INACTIVE_BUTTON_COLOR))
        else:
            self.window.bkgd(" ", curses.color_pair(Color.ACTIVE_BUTTON_COLOR))
        self.window.refresh()

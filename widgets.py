import curses
import re
from abc import ABC, abstractmethod

from consts import Color


class Widget(ABC):
    def __init__(self, parent, border_top, border_left, index, caption, mode):
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
    def __init__(self, parent, border_top, border_left, index, caption, mode):
        super().__init__(parent, border_top, border_left, index, caption, mode)
        height, width = self.window.getmaxyx()
        self.width = width - 2 - 1
        self.cursor_pos = 0
        self.window.keypad(True)
        self.value = ''

    def show(self):
        self.window.hline(self.y, self.x, ' ', self.width)
        display_text = self.value[:self.width]
        self.window.bkgd(' ', self.color)
        self.window.addstr(self.y, self.x, display_text)
        cursor_x = self.x + self.cursor_pos
        self.window.move(self.y, cursor_x)
        self.window.refresh()

    def handle_input(self, key):
        self.color = curses.color_pair(Color.EDITOR_COLOR)
        if key == curses.KEY_LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
        elif key == curses.KEY_RIGHT:
            if self.cursor_pos < len(self.value):
                self.cursor_pos += 1
        elif key == curses.KEY_BACKSPACE:
            if self.cursor_pos > 0:
                self.value = self.value[:self.cursor_pos - 1] + self.value[self.cursor_pos:]
                self.cursor_pos -= 1
        elif key == curses.KEY_DC:
            if self.cursor_pos > 0:
                self.value = self.value[:self.cursor_pos] + self.value[self.cursor_pos + 1:]
        elif 32 <= key < 127:
            if len(self.value) < self.width:
                self.value = self.value[:self.cursor_pos] + chr(key) + self.value[self.cursor_pos:]
                self.cursor_pos += 1


class Checkbox(Widget):
    def __init__(self, parent, border_top, border_left, index, caption, mode):
        super().__init__(parent, border_top, border_left, index, caption, mode)
        self.value = False

    def show(self):
        checkbox_str = " [X] ON " if self.value else " [ ] OFF"
        self.window.addstr(self.y, self.x, checkbox_str)
        self.window.refresh()

    def toggle(self):
        self.value = not self.value

    def is_checked(self):
        return self.value


class RadioGroupState(Widget):
    def __init__(self, parent, border_top, border_left, index, caption, mode):
        super().__init__(parent, border_top, border_left, index, caption, mode)
        self.options = ['UP', 'DOWN']
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
        current_x = self.x
        for idx, option in enumerate(self.options):
            if idx == self.selected_index:
                prefix = " (*)"
                line = f"{prefix} {option}"
                mode = curses.A_REVERSE
            else:
                prefix = " ( )"
                line = f"{prefix} {option}"
                mode = curses.A_NORMAL

            self.window.addstr(self.y, current_x, line, mode)

            current_x += len(line) + self.spacing
        self.window.refresh()

    def handle_input(self, key):
        if key == curses.KEY_LEFT:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == curses.KEY_RIGHT:
            self.selected_index = min(len(self.options) - 1, self.selected_index + 1)


class Button:
    def __init__(self, parent, border_top, border_left, index, caption, mode):
        self.parent = parent
        y, x = self.parent.getmaxyx()
        self.y = border_top + index + border_top * index + 2
        self.caption = f"    {caption}    "
        # self.window = self.parent.subwin(self.y, x, border_top, border_left)
        self.x = (border_left + 21) // 2 - len(self.caption) // 2
        self.value = lambda: None
        self.mode = mode

    def show(self):
        if self.mode == curses.A_NORMAL:
            self.parent.addstr(
                self.y, self.x, self.caption, curses.color_pair(Color.INACTIVE_BUTTON_COLOR) | curses.A_BOLD
            )
        else:
            self.parent.addstr(
                self.y, self.x, self.caption, curses.color_pair(Color.ACTIVE_BUTTON_COLOR) | curses.A_BOLD
            )


class IPTextEdit:
    def __init__(self, stdscr, y, x):
        self.stdscr = stdscr
        self.y = y
        self.x = x
        self.mask = "_._._._"
        self.editable_positions = [i for i, c in enumerate(self.mask) if c == '_']
        self._value = [''] * len(self.editable_positions)
        self.current_field = 0

    def show(self):
        display = list(self.mask)
        for idx, pos in enumerate(self.editable_positions):
            if self._value[idx]:
                display[pos] = self._value[idx]
        display_str = ''.join(display)

        # Очищаем строку и выводим текущий IP с маской
        self.stdscr.hline(self.y, self.x, ' ', len(display_str))
        self.stdscr.addstr(self.y, self.x, display_str)

        # Устанавливаем курсор на текущую позицию
        cursor_pos = self.editable_positions[self.current_field]
        self.stdscr.move(self.y, self.x + cursor_pos)

    def handle_input(self, ch):
        if ch == curses.KEY_LEFT:
            if self.current_field > 0:
                self.current_field -= 1
        elif ch == curses.KEY_RIGHT:
            if self.current_field < len(self.editable_positions) - 1:
                self.current_field += 1
        elif ch == 8 or ch == 127:  # Backspace
            field_idx = self.current_field
            if self._value[field_idx]:
                self._value[field_idx] = ''
            elif field_idx > 0:
                self.current_field -= 1
                self._value[self.current_field] = ''
        elif 48 <= ch <= 57:  # Цифра
            digit = chr(ch)
            field_idx = self.current_field
            self._value[field_idx] = digit
            # Автоматический переход к следующему полю, если возможно
            if field_idx < len(self.editable_positions) - 1:
                self.current_field += 1

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value:
            self._value = list(value)
        else:
            self._value = [''] * len(self.editable_positions)

    def get_ip(self):
        parts = []
        for val in self._value:
            if not val:
                return None
            parts.append(val)
        return ".".join(parts)

    def is_valid_ip(self):
        ip = self.get_ip()
        if not ip:
            return False
        pattern = re.compile(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
        return bool(pattern.match(ip))

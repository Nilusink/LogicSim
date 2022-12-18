"""
interactions.py
14. December 2022

A few GUI classes that have nothing to do with logic

Author:
Nilusink
"""
from contextlib import suppress

import time
import pygame as pg
import typing as tp

from ..basegame.game import BaseGame
from ...additional.classes import Vec2
from ..basegame.groups import Drawn, Updated, Gates
from .lines import Line


class Point(pg.sprite.Sprite):
    _pos: Vec2
    radius: float
    color: tuple[float, float, float, float]

    def __init__(
            self,
            origin: tuple[float | int, float | int] | Vec2,
            color: tuple[float, float, float, float] = ...,
            radius: float = 10,
            hidden: bool = False,
    ):
        self.position = origin
        if color is ...:
            self.color = (255, 255, 255, 255)

        else:
            self.color = color

        self.radius = radius
        self._hidden = hidden

        super().__init__()
        Drawn.add(self)

    def draw(self, surface: pg.Surface):
        """
        how the point should be represented
        """
        if not self._hidden:
            mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())

            pg.draw.circle(
                surface,
                (200, 100, 100, 255) if self.check_collision(mouse_pos) else self.color,
                self.position.xy,
                self.radius,
            )

    @property
    def position(self) -> Vec2:
        """
        the points current position
        """
        return self._pos.copy()

    @position.setter
    def position(self, pos: tuple[float | int, float | int] | Vec2):
        """
        set the points current position
        """
        if not issubclass(type(pos), Vec2):
            pos = Vec2.from_cartesian(*pos)

        self._pos = pos.copy()

    def check_collision(self, point: Vec2):
        """
        check if the point is inside the hit-box
        """
        delta = self.position - point

        return delta.length <= self.radius


class DraggablePoint(Point):
    _live_follow: bool = False
    _mouse_delta_on_start: Vec2 = ...

    def __init__(
            self,
            origin: tuple[float | int, float | int] | Vec2,
            color: tuple[float, float, float, float] = ...,
            radius: float = 10,
    ):
        # mutable inits
        self._mouse_delta_on_start = Vec2()

        # initialize pygame stuff
        super().__init__(origin, color, radius)
        Updated.add(self)

        # create hooks
        BaseGame.on_event(pg.MOUSEBUTTONDOWN, self.start_follow)
        BaseGame.on_event(pg.MOUSEBUTTONUP, self.stop_follow)

    def update(self, _delta: float):
        """
        basic updates needed
        """
        if self._live_follow and not BaseGame.stop_listen():
            self.position = Vec2.from_cartesian(*pg.mouse.get_pos()) + self._mouse_delta_on_start

    def start_follow(self, event=...):
        """
        start the following of the mouse cursor
        """
        if event is ...:
            self._live_follow = True
            self._mouse_delta_on_start = Vec2()
            return

        if event.button == 1:
            mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())

            if self.check_collision(mouse_pos):
                self._live_follow = True
                self._mouse_delta_on_start = self.position - mouse_pos

    def stop_follow(self, event):
        """
        stop the following of the mouse cursor
        """
        if event.button == 1:
            self._live_follow = False


class LinePoint(Point):
    _connected_lines: list[Line]
    _state: bool = False

    def __init__(self, *args, **kwargs):
        """
        a point that triggers a line on creation
        """
        self._connected_lines = []
        self._parent = kwargs.pop("parent")
        self._type = kwargs.pop("type")
        self._pid = kwargs.pop("id")

        if "update_parent" in kwargs.keys():
            self.update_parent = kwargs.pop("update_parent")

        else:
            self.update_parent = True

        self._id = f"{self._parent.id}{self._type}{self._pid}"

        super().__init__(*args, **kwargs)

        self._event_id = BaseGame.on_event(pg.MOUSEBUTTONDOWN, self.on_click)

    @property
    def parent(self):
        return self._parent

    @property
    def state(self):
        return self._state

    @property
    def id(self) -> str:
        return self._id

    @property
    def connected_lines(self) -> list[Line]:
        return self._connected_lines.copy()

    @property
    def position(self) -> Vec2:
        """
        the points current position
        """
        return self._pos.copy()

    @position.setter
    def position(self, pos: tuple[float | int, float | int] | Vec2):
        """
        set the points current position
        """
        if not issubclass(type(pos), Vec2):
            pos = Vec2.from_cartesian(*pos)

        self._pos = pos.copy()

        for line in self._connected_lines:
            with suppress(IndexError):
                if "o" in self._type:
                    line.set_points[0] = self.position
                    continue

                line.set_points[-1] = self.position

    def add_connection(self, line: Line):
        self._connected_lines.append(line)

    def on_click(self, _event):
        """
        for drawing lines
        """
        if not self._hidden and not BaseGame.stop_listen():
            mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())

            if self.check_collision(mouse_pos):
                if BaseGame.globals.drawing_line is not None and \
                        "i" in self._type and len(self._connected_lines) == 0:
                    line: Line = BaseGame.globals.drawing_line

                    if not line.set_points[0] == self.position:
                        line.add(self.position)
                        line.set_target(self)

                        line.finish()

                        self._connected_lines.append(line)
                        BaseGame.globals.drawing_line = None
                        return

                if "o" in self._type and BaseGame.globals.drawing_line is None:
                    line = Line(self.position, self)
                    BaseGame.globals.drawing_line = line
                    self._connected_lines.append(line)

    def update_input(self, value: bool):
        """
        update a point that is an input
        """
        if "i" not in self._type:
            return
            # raise RuntimeError("can only update the input values of an input gate")

        self._state = value

        if self.update_parent:
            self.parent.update_input(self._pid, value)

    def update_connections(self, value: bool):
        """
        update all connected points (gates)
        """
        if "o" not in self._type:
            return
            # raise RuntimeError("can only update from an output")

        # update points
        for line in self._connected_lines:
            line.active = value

    def delete(self):
        """
        remove and destroy the button
        """
        BaseGame.clear_on_event(self._event_id)
        with suppress(KeyError):
            Drawn.remove(self)


class Button(pg.sprite.Sprite):
    _position: Vec2
    _size: Vec2

    text: str
    bg: tuple[float, float, float, float]
    fg: tuple[float, float, float, float]
    active_bg: tuple[float, float, float, float]
    active_fg: tuple[float, float, float, float]

    def __init__(
            self,
            position: tuple[float | int, float | int] | Vec2,
            size: tuple[float | int, float | int] | Vec2,
            bg: tuple[float, float, float, float] = ...,
            fg: tuple[float, float, float, float] = ...,
            active_bg: tuple[float, float, float, float] = ...,
            active_fg: tuple[float, float, float, float] = ...,
            on_click: tp.Callable = ...,
            text: str = ...,
    ):
        if not issubclass(type(position), Vec2):
            position = Vec2.from_cartesian(*position)

        if not issubclass(type(size), Vec2):
            size = Vec2.from_cartesian(*size)

        if bg is ...:
            bg = (70, 70, 70, 255)

        if fg is ...:
            fg = (255, 255, 255, 255)

        if active_bg is ...:
            active_bg = (90, 90, 90, 255)

        if active_fg is ...:
            active_fg = (255, 255, 255, 255)

        if text is ...:
            text = "Button"

        self._on_click = on_click
        self.active_bg = active_bg
        self.active_fg = active_fg
        self._position = position
        self._size = size
        self.text = text
        self.bg = bg
        self.fg = fg

        super().__init__()
        Drawn.add(self)

        self.__event_id = BaseGame.on_event(pg.MOUSEBUTTONDOWN, self.__on_click)

    @property
    def position(self) -> Vec2:
        return self._position

    def __on_click(self, event: pg.event.Event):
        """
        called by an event, executes the on_click function
        """
        if self.check_collision(Vec2.from_cartesian(*pg.mouse.get_pos())):
            if self._on_click is not ... and not BaseGame.stop_listen():
                self._on_click(event)

    def check_collision(self, point: Vec2) -> bool:
        """
        check if a point collides with the button
        """
        x = self._position.x <= point.x <= self._position.x + self._size.x
        y = self._position.y <= point.y <= self._position.y + self._size.y

        return x and y

    def draw(self, _surface: pg.Surface):
        """
        draw the button on the screen
        """
        mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())

        hover = self.check_collision(mouse_pos) and not BaseGame.stop_listen()

        pg.draw.rect(
            BaseGame.lowest_layer,
            self.active_bg if hover else self.bg,
            pg.Rect(
                *self._position.xy,
                *self._size.xy,
            ),
        )

        # draw text
        text = BaseGame.font.render(self.text, True, self.active_fg if hover else self.fg)
        text_rect = text.get_rect()

        text_rect.center = (self._position + (self._size / 2)).xy

        BaseGame.lowest_layer.blit(text, text_rect)

    def kill(self):
        """
        properly dismisses the button
        """
        BaseGame.clear_on_event(self.__event_id)
        Drawn.remove(self)

    def delete(self):
        """
        completely remove the button
        """
        Drawn.remove(self)
        with suppress(KeyError):
            BaseGame.clear_on_event(self.__event_id)


class Focusable(pg.sprite.Sprite):
    __focused: bool = False

    def __init__(self, focused: bool = False):
        super().__init__()
        self.focused = focused

    @property
    def focused(self) -> bool:
        return self.__focused

    @focused.setter
    def focused(self, value: bool):
        """
        set or not set the focus of the entry
        """
        if value:
            if BaseGame.globals.focused in (self, None):
                BaseGame.globals.focused = self
                self.__focused = True
                return

            BaseGame.globals.focused.focused = False
            BaseGame.globals.focused = self
            self.__focused = True
            return

        if BaseGame.globals.focused is self:
            BaseGame.globals.focused = None

        self.__focused = False


class Entry(Focusable):
    """
    a basic entry (thing where you can type)
    """
    bg: tuple[int, int, int, int]
    active_bg: tuple[int, int, int, int]
    fg: tuple[int, int, int, int]
    active_fg: tuple[int, int, int, int]
    cursor_color: tuple[int, int, int, int]
    border_radius: int

    _focused: bool = False
    _cursor_pos: int = 0
    __text: str = ""
    _position: Vec2
    _size: Vec2

    def __init__(
            self,
            position: tuple[int | float, int | float] | Vec2,
            size: tuple[int | float, int | float] | Vec2,
            bg: tuple[int, int, int, int] = ...,
            active_bg: tuple[int, int, int, int] = ...,
            fg: tuple[int, int, int, int] = ...,
            active_fg: tuple[int, int, int, int] = ...,
            cursor_color: tuple[int, int, int, int] = ...,
            border_radius: int = -1,
            focused: bool = False,
    ):
        # default arguments
        if bg is ...:
            bg = (60, 60, 60, 255)

        if active_bg is ...:
            active_bg = (70, 70, 70, 255)

        if fg is ...:
            fg = (200, 200, 200, 255)

        if active_fg is ...:
            active_fg = (255, 255, 255, 255)

        if cursor_color is ...:
            cursor_color = (255, 255, 255, 255)

        self.bg = bg
        self.active_bg = active_bg
        self.fg = fg
        self.active_fg = active_fg
        self.cursor_color = cursor_color
        self.border_radius = border_radius

        self.position = position
        self.size = size

        super().__init__(focused)
        Drawn.add(self)

        self.__event_ids: list[int] = []
        self.__event_ids.append(BaseGame.on_event(pg.KEYDOWN, self.on_keypress))
        self.__event_ids.append(BaseGame.on_event(pg.MOUSEBUTTONDOWN, self.on_mouse_button_down))

    @property
    def text(self) -> str:
        """
        the text present in the entry
        """
        return self.__text

    @text.setter
    def text(self, value: str):
        """
        the text present in the entry
        """
        self.__text = value
        self._cursor_pos = len(self.text)

    @property
    def position(self) -> Vec2:
        """
        The entries current position
        """
        return self._position

    @position.setter
    def position(self, value: tuple[int | float, int | float] | Vec2):
        """
        set the entries current position
        """
        if not issubclass(value.__class__, Vec2):
            value = Vec2.from_cartesian(*value)

        self._position = value

    @property
    def size(self) -> Vec2:
        """
        The entries current size
        """
        return self._size

    @size.setter
    def size(self, value: tuple[int | float, int | float] | Vec2):
        """
        set th entries current size
        """
        if not issubclass(value.__class__, Vec2):
            value = Vec2.from_cartesian(*value)

        self._size = value

    def draw(self, surface: pg.Surface):
        """
        draw the entry
        """
        # draw background
        pg.draw.rect(
            surface,
            self.active_bg if self.focused else self.bg,
            pg.Rect(*self.position.xy, *self.size.xy),
            0,
            self.border_radius,
        )

        # draw text
        text = BaseGame.font.render(self.text, True, self.active_fg if self.focused else self.fg)
        text_rect = text.get_rect()

        text_rect.center = (self.position + self.size / 2).xy

        surface.blit(text, text_rect)

        blink = int(str(time.time()).split(".")[-1][0]) < 5

        # if focused, draw cursor
        if self.focused and blink:
            sample_text = BaseGame.font.render(self.text[:self._cursor_pos], True, self.fg)
            sample_rect = sample_text.get_rect()

            cursor_pos = [text_rect.x + sample_rect.size[0], self.position.y]
            cursor_pos[1] += int(self.size.y / 10)

            size = (5, self.size.y * .8)

            pg.draw.rect(surface, self.cursor_color, pg.Rect(*cursor_pos, *size))

    def check_collision(self, position: Vec2) -> bool:
        """
        check if a point collides with the entry
        """
        x = self.position.x <= position.x <= self.position.x + self.size.x
        y = self.position.y <= position.y <= self.position.y + self.size.y

        return x and y

    def on_keypress(self, event: pg.event.Event):
        """
        record a keypress
        """
        if BaseGame.globals.focused == self:
            # for deleting
            match event.key:
                case pg.K_BACKSPACE:
                    if self._cursor_pos > 0:
                        self.__text = self.text[:(self._cursor_pos-1)] + self.text[self._cursor_pos:]
                        self._cursor_pos -= 1

                case pg.K_LEFT:
                    if self._cursor_pos > 0:
                        self._cursor_pos -= 1

                case pg.K_RIGHT:
                    if self._cursor_pos < len(self.text):
                        self._cursor_pos += 1

                case _:
                    # check if space is held
                    mods = pg.key.get_mods()
                    shift = mods & pg.KMOD_SHIFT
                    ctrl = mods & pg.KMOD_CTRL

                    # if control is held
                    if ctrl:
                        return

                    # convert to character
                    with suppress(ValueError):
                        character = chr(event.key)
                        if shift:
                            character = character.upper()

                        self.__text = self.text[:self._cursor_pos] + character + self.text[self._cursor_pos:]
                        self._cursor_pos += 1

    def on_mouse_button_down(self, *_trash):
        """
        set or remove focus
        """
        mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())

        if self.check_collision(mouse_pos) and BaseGame.globals.focused is None:
            self.focused = True
            return

        if BaseGame.globals.focused == self:
            self.focused = False

    def delete(self):
        """
        completely remove the entry
        """
        for eid in self.__event_ids:
            BaseGame.clear_on_event(eid)
        Drawn.remove(self)


class CircularButton(Button):
    def __init__(
            self,
            position: tuple[float | int, float | int] | Vec2,
            radius: float,
            bg: tuple[float, float, float, float] = ...,
            fg: tuple[float, float, float, float] = ...,
            active_bg: tuple[float, float, float, float] = ...,
            active_fg: tuple[float, float, float, float] = ...,
            on_click: tp.Callable = ...,
            text: str = ...,
    ):
        if active_bg is ...:
            active_bg = (255, 100, 100, 255)

        self._radius = radius

        super().__init__(
            position,
            (radius,) * 2,
            bg,
            fg,
            active_bg,
            active_fg,
            on_click,
            text,
        )

    def draw(self, surface: pg.Surface):
        """
        draw the button on the screen
        """
        mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())

        hover = self.check_collision(mouse_pos)

        pg.draw.circle(
            surface,
            self.active_bg if hover else self.bg,
            self._position.xy,
            self._radius,
        )

        # draw text
        text = BaseGame.font.render(self.text, True, self.active_fg if hover else self.fg)
        text_rect = text.get_rect()

        text_rect.center = (self._position + (self._size / 2)).xy

        BaseGame.lowest_layer.blit(text, text_rect)


class IOToggleButton(pg.sprite.Sprite):
    _state: bool = False

    def __init__(
            self,
            position: tuple[float | int, float | int] | Vec2,
            output_position: tuple[float | int, float | int] | Vec2,
            parent,
            pid: int,
            type: str,
    ):
        self._parent = parent

        super().__init__()

        self.cb = CircularButton(
            position if type == "o" else output_position,
            radius=30,
            on_click=self.on_toggle,
            text="",
            bg=(70, 70, 70, 255),
            active_bg=(100, 100, 100, 255),
        )

        self.lb = LinePoint(
            output_position if type == "o" else position,
            parent=parent,
            id=pid,
            type=type,
        )
        Drawn.remove(self.cb)
        Drawn.remove(self.lb)
        Drawn.add(self)

    def set_state(self, value: bool):
        self._state = value
        self._update()

    def on_toggle(self, *_trash):
        # actual toggling
        self._state = not self._state
        self._update()

    def _update(self):
        if self._state:
            self.cb.bg = (255, 70, 70, 255)
            self.cb.active_bg = (255, 100, 100, 255)

        else:
            self.cb.bg = (70, 70, 70, 255)
            self.cb.active_bg = (100, 100, 100, 255)

        # update parent
        self.lb.update_connections(self._state)

    def draw(self, surface: pg.Surface):
        pg.draw.line(surface, (0, 0, 0, 255), self.cb.position.xy, self.lb.position.xy, 5)

        self.cb.draw(surface)
        self.lb.draw(surface)

    def delete(self):
        """
        completely remove the ToggleButton
        """
        Drawn.remove(self)
        self.cb.delete()
        self.lb.delete()
        self.kill()


class IOBox(pg.sprite.Sprite):
    _pos: Vec2
    size: Vec2
    _id: int

    _inputs: list[IOToggleButton]

    instance: "IOBox" = None

    def __new__(cls, *args, **kwargs):
        new = super().__new__(cls)

        if cls.instance is not None:
            raise RuntimeError(f"only on instance of type \"{cls.__name__}\" can exist!")

        cls.instance = new

        return new

    def __init__(
            self,
            position: tuple[float | int, float | int] | Vec2,
            size: tuple[float | int, float | int] | Vec2,
    ):
        self._id = -1

        if not issubclass(type(size), Vec2):
            size = Vec2.from_cartesian(*size)

        self.position = position
        self._inputs = []
        self.size = size

        super().__init__()
        Drawn.add(self)

        BaseGame.on_event(pg.MOUSEBUTTONDOWN, self.on_click)

    @property
    def id(self) -> int:
        return self._id

    @property
    def position(self) -> Vec2:
        return self._pos

    @position.setter
    def position(self, value: tuple[float | int, float | int] | Vec2):
        if not issubclass(type(value), Vec2):
            value = Vec2.from_cartesian(*value)

        self._pos = value

    @property
    def inputs(self) -> list[IOToggleButton]:
        return self._inputs.copy()

    def check_collision(self, point: Vec2):
        """
        check if a point is within the hit-box
        """
        x = self.position.x <= point.x <= self.position.x + self.size.x
        y = self.position.y <= point.y <= self.position.y + self.size.y

        return x and y

    def draw(self, surface: pg.Surface):
        """
        draw the box
        """
        mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())

        pg.draw.rect(BaseGame.lowest_layer, (60, 60, 60, 255), pg.Rect(*self.position.xy, *self.size.xy))

        if self.check_collision(mouse_pos) and not BaseGame.stop_listen():
            c_pos = (
                self.position.x + self.size.x / 2,
                mouse_pos.y
            )
            pg.draw.circle(surface, (80, 80, 80, 255), c_pos, 20)

    def on_click(self, _event: pg.event.Event):
        ...

    def add_input(self, y_position: int | float):
        ...

    def clear(self):
        """
        remove all inputs / outputs
        """
        inp = self.inputs
        self._inputs.clear()

        for inn in inp:
            inn.delete()
            del inn


class InputsBox(IOBox):
    id = -1

    def __init__(
            self,
            position: tuple[float | int, float | int] | Vec2,
            size: tuple[float | int, float | int] | Vec2,
    ):
        super().__init__(position, size)

    def on_click(self, _event: pg.event.Event):
        mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())

        if self.check_collision(mouse_pos):
            self._inputs.append(IOToggleButton(
                (self.position.x - 45, mouse_pos.y),
                (self.position.x + self.size.x + 15, mouse_pos.y),
                parent=self,
                pid=len(self._inputs),
                type="o",
            ))

    def add_input(self, y_position: int | float):
        self._inputs.append(IOToggleButton(
                    (self.position.x - 45, y_position),
                    (self.position.x + self.size.x + 15, y_position),
                    parent=self,
                    pid=len(self._inputs),
                    type="o",
                )
            )


class OutputsBox(IOBox):
    id = -2

    def __init__(
            self,
            position: tuple[float | int, float | int] | Vec2,
            size: tuple[float | int, float | int] | Vec2,
    ):
        super().__init__(position, size)

    def on_click(self, _event: pg.event.Event):
        mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())

        if self.check_collision(mouse_pos):
            self._inputs.append(IOToggleButton(
                (self.position.x - 45, mouse_pos.y),
                (self.position.x + self.size.x + 15, mouse_pos.y),
                parent=self,
                pid=len(self._inputs),
                type="i",
            ))

    def add_input(self, y_position: int | float):
        self._inputs.append(
            IOToggleButton(
                (self.position.x - 45, y_position),
                (self.position.x + self.size.x + 15, y_position),
                parent=self,
                pid=len(self._inputs),
                type="i",
            )
        )

    def update_input(self, id: int, value: bool):
        self._inputs[id].set_state(value)

"""
interactions.py
14. December 2022

A few GUI classes that have nothing to do with logic

Author:
Nilusink
"""
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
    ):
        self.position = origin
        if color is ...:
            self.color = (255, 255, 255, 255)

        else:
            self.color = color

        self.radius = radius

        super().__init__()
        Drawn.add(self)

    def draw(self, surface: pg.Surface):
        """
        how the point should be represented
        """
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
        if self._live_follow:
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

        self._id = f"{self._parent.id}{self._type}{self._pid}"

        super().__init__(*args, **kwargs)

        BaseGame.on_event(pg.MOUSEBUTTONDOWN, self.on_click)

    @property
    def parent(self):
        return self._parent

    @property
    def state(self):
        return self._state

    def on_click(self, _event):
        """
        for drawing lines
        """
        mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())

        if self.check_collision(mouse_pos):
            if BaseGame.globals.drawing_line is not None and \
                    self._type == "i" and len(self._connected_lines) == 0:
                line: Line = BaseGame.globals.drawing_line

                if not line.set_points[0] == self.position:
                    line.add(self.position)
                    line.set_target(self)

                    line.finish()

                    self._connected_lines.append(line)
                    BaseGame.globals.drawing_line = None
                    return

            if self._type == "o" and BaseGame.globals.drawing_line is None:
                line = Line(self.position, self)
                BaseGame.globals.drawing_line = line
                self._connected_lines.append(line)

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
            if self._type == "o":
                line.set_points[0] = self.position
                continue

            line.set_points[-1] = self.position

    def update_input(self, value: bool):
        """
        update a point that is an input
        """
        if not self._type == "i":
            return
            # raise RuntimeError("can only update the input values of an input gate")

        self._state = value
        self.parent.update_input(self._pid, value)

    def update_connections(self, value: bool):
        """
        update all connected points (gates)
        """
        if not self._type == "o":
            return
            # raise RuntimeError("can only update from an output")

        # update points
        for line in self._connected_lines:
            line.active = value


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
            if self._on_click is not ...:
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

        hover = self.check_collision(mouse_pos)

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


class IOBox(pg.sprite.Sprite):
    _pos: Vec2
    size: Vec2
    _id: int

    _inputs: list[IOToggleButton]

    def __init__(
            self,
            position: tuple[float | int, float | int] | Vec2,
            size: tuple[float | int, float | int] | Vec2,
    ):
        self._id = Gates.yield_unique_id()

        if not issubclass(type(size), Vec2):
            size = Vec2.from_cartesian(*size)

        self.position = position
        self._inputs = []
        self.size = size

        super().__init__()
        Drawn.add(self)
        Gates.add(self)

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

        if self.check_collision(mouse_pos):
            c_pos = (
                self.position.x + self.size.x / 2,
                mouse_pos.y
            )
            pg.draw.circle(surface, (80, 80, 80, 255), c_pos, 20)

    def on_click(self, _event: pg.event.Event):
        ...


class InputsBox(IOBox):
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
                pid="0",
                type="o",
            ))


class OutputsBox(IOBox):
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

    def update_input(self, id: int, value: bool):
        self._inputs[id].set_state(value)

"""
logic.py
13. December 2022

adds basic and modular logic stuff

Author:
Nilusink
"""
from contextlib import suppress

import pygame as pg
import typing as tp

from ..basegame.game import BaseGame
from ...additional.classes import Vec2
from ..basegame.groups import Gates, Updated, Drawn
from .interactions import LinePoint, DraggablePoint


class Base(DraggablePoint):
    """
    basic logic element
    """
    _size: Vec2
    port_size: float = 10
    port_states: list[bool]

    _input_points: list[LinePoint]
    _output_points: list[LinePoint]

    __initial_args: tuple[tuple[float | int, float | int] | Vec2, str, tp.Callable, int, int]

    def __init__(
            self,
            position: tuple[float | int, float | int] | Vec2,
            name: str,
            logic_func: tp.Callable,
            inputs: int,
            outputs: int
    ):
        self.__id = Gates.yield_unique_id()

        if not issubclass(type(position), Vec2):
            position = Vec2.from_cartesian(*position)

        self.__initial_args = (position.copy(), name, logic_func, inputs, outputs)

        self.port_states = [False] * inputs

        self._input_points = []
        self._output_points = []

        self._size = Vec2.from_cartesian(100, self.port_size * ((max(inputs, outputs) + 1) * 2))

        self._name = name
        self._inputs = inputs
        self._outputs = outputs
        self._logic_func = logic_func

        super().__init__(position)
        # Updated.add(self)
        Gates.add(self)

        # setup buttons and stuff
        self._port_setup()

        self.__event_id = BaseGame.on_event(pg.MOUSEBUTTONDOWN, self.on_mouse_down)

    def _port_setup(self):
        # setup ports
        for i in range(self._inputs):
            off = self._size.y / (self._inputs * 2)
            z = self.position.y - self._size.y / 2
            y = z + off + off * i * 2

            self._input_points.append(
                LinePoint(
                    Vec2.from_cartesian(self.position.x - self._size.x / 2, y),
                    radius=self.port_size,
                    color=(100, 100, 100, 255),
                    parent=self,
                    type="i",
                    id=i,
                )
            )

        for i in range(self._outputs):
            off = self._size.y / (self._outputs * 2)
            z = self.position.y - self._size.y / 2
            y = z + off + off * i * 2

            self._output_points.append(
                LinePoint(
                    Vec2.from_cartesian(self.position.x + self._size.x / 2, y),
                    radius=self.port_size,
                    color=(100, 100, 100, 255),
                    parent=self,
                    type="o",
                    id=i,
                )
            )

    @property
    def name(self) -> str:
        return self._name

    @property
    def initial_args(self) -> tuple[tuple[float | int, float | int] | Vec2, str, tp.Callable, int, int]:
        return self.__initial_args

    @property
    def id(self) -> int:
        """
        the gates unique id
        """
        return self.__id

    @property
    def input_points(self) -> list[LinePoint]:
        return self._input_points

    @property
    def output_points(self) -> list[LinePoint]:
        return self._output_points

    def draw(self, surface: pg.Surface):
        """
        draws the gate
        """
        self.update_logic()

        mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())
        hover = self.check_collision(mouse_pos) and not BaseGame.stop_listen()

        if hover and pg.key.get_pressed()[pg.K_DELETE]:
            self.delete()
            return

        p0x = self.position.x - self._size.x / 2
        p0y = self.position.y - self._size.y / 2

        # draw rect
        pg.draw.rect(
            surface, self.color, pg.Rect(
                p0x, p0y,
                *self._size.xy,
            ),
            border_radius=10,
        )

        # draw text
        text = BaseGame.font.render(self._name, True, (0, 0, 0, 255))
        text_rect = text.get_rect()

        text_rect.center = self.position.xy

        surface.blit(text, text_rect)

    def update_logic(self, *_trash):
        result: tuple[bool] | bool = self._logic_func(*self.port_states)

        if issubclass(type(result), tuple):
            with suppress(IndexError):
                for i in range(len(result)):
                    self._output_points[i].update_connections(result[i])

            return

        self._output_points[0].update_connections(result)

    def check_collision(self, point: Vec2):
        """
        check if the point is inside the hit-box
        """
        x = self.position.x - self._size.x / 2 <= point.x <= self.position.x + self._size.x / 2
        y = self.position.y - self._size.y / 2 <= point.y <= self.position.y + self._size.y / 2

        return x and y

    def on_mouse_down(self, event: pg.event.Event):
        """

        """
        mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())
        hover = self.check_collision(mouse_pos) and not BaseGame.stop_listen()

        if hover:
            if event.button == 2:
                with suppress(FileNotFoundError):
                    BaseGame.globals.load_file_func(f"./blocks/{self.name}.json")

                    if BaseGame.globals.name_entry is not ...:
                        BaseGame.globals.name_entry.text = self.name

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

        # update input points
        for i in range(len(self._input_points)):
            off = self._size.y / (self._inputs * 2)
            z = self.position.y - self._size.y / 2
            y = z + off + off * i * 2

            self._input_points[i].position = Vec2.from_cartesian(self.position.x - self._size.x / 2, y)

        # update output points
        for i in range(len(self._output_points)):
            off = self._size.y / (self._outputs * 2)
            z = self.position.y - self._size.y / 2
            y = z + off + off * i * 2

            self._output_points[i].position = Vec2.from_cartesian(self.position.x + self._size.x / 2, y)

    def update_input(self, input_id: int, value: bool):
        """
        update the logic gate
        """
        self.port_states[input_id] = value

    def delete(self):
        """
        removes the gate
        """
        # delete connected wires
        for point in self._output_points:
            for line in point.connected_lines:
                line.delete()
            point.delete()

        for point in self._input_points:
            for line in point.connected_lines:
                line.delete()
            point.delete()

        # remove self
        Updated.remove(self)
        Drawn.remove(self)

        del self

    def __call__(self, *args, **kwargs):
        return self._logic_func(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<Block {self.__class__.__name__}, id={self.id}>"


class And(Base):
    def __init__(self, position: Vec2):
        self.__initial_args: tuple[Vec2] = (position.copy(),)
        super().__init__(position, "And", self.logic_func, 2, 1)

    @staticmethod
    def logic_func(x: bool, y: bool) -> bool:
        return x and y

    @property
    def initial_args(self) -> tuple[Vec2]:
        return self.__initial_args


class Not(Base):
    def __init__(self, position: Vec2):
        self.__initial_args: tuple[Vec2] = (position.copy(),)
        super().__init__(position, "Not", self.logic_func, 1, 1)

    @staticmethod
    def logic_func(x: bool) -> bool:
        return not x

    @property
    def initial_args(self) -> tuple[Vec2]:
        return self.__initial_args


class CustomBlock(Base):
    _input_output_points: list[LinePoint]
    _output_input_points: list[LinePoint]

    def __init__(
            self,
            position: tuple[float | int, float | int] | Vec2,
            name: str,
            logic_func: tp.Union[tp.Callable, None],
            inputs: int,
            outputs: int
    ):
        self._input_output_points = []
        self._output_input_points = []

        super().__init__(position, name, logic_func, inputs, outputs)

        # setup ports
        for i in range(self._inputs):
            off = self._size.y / (self._inputs * 2)
            z = self.position.y - self._size.y / 2
            y = z + off + off * i * 2

            self._input_output_points.append(
                LinePoint(
                    Vec2.from_cartesian(self.position.x - self._size.x / 2, y),
                    radius=self.port_size,
                    color=(100, 100, 100, 255),
                    parent=self,
                    type="co",
                    id=i,
                    hidden=True,
                    update_parent=False,
                )
            )

        for i in range(self._outputs):
            off = self._size.y / (self._outputs * 2)
            z = self.position.y - self._size.y / 2
            y = z + off + off * i * 2

            self._output_input_points.append(
                LinePoint(
                    Vec2.from_cartesian(self.position.x + self._size.x / 2, y),
                    radius=self.port_size,
                    color=(100, 100, 100, 255),
                    parent=self,
                    type="ci",
                    id=i,
                    hidden=True,
                    update_parent=False,
                )
            )

    def update_input(self, input_id: int, value: bool):
        """
        update the logic gate
        """
        self.port_states[input_id] = value
        self._input_output_points[input_id].update_connections(value)

    def update_logic(self, *_trash):
        with suppress(IndexError):
            for i in range(self._outputs):
                self._output_points[i].update_connections(self._output_input_points[i].state)

    @property
    def input_output_points(self) -> list[LinePoint]:
        return self._input_output_points.copy()

    @property
    def output_input_points(self) -> list[LinePoint]:
        return self._output_input_points.copy()

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

        # update input points
        for i in range(len(self._input_points)):
            off = self._size.y / (self._inputs * 2)
            z = self.position.y - self._size.y / 2
            y = z + off + off * i * 2

            self._input_points[i].position = Vec2.from_cartesian(self.position.x - self._size.x / 2, y)
            self._input_output_points[i].position = self._input_points[i].position

        # update output points
        for i in range(len(self._output_points)):
            off = self._size.y / (self._outputs * 2)
            z = self.position.y - self._size.y / 2
            y = z + off + off * i * 2

            self._output_points[i].position = Vec2.from_cartesian(self.position.x + self._size.x / 2, y)
            self._output_input_points[i].position = self._output_points[i].position

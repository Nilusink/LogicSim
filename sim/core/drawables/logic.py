"""
logic.py
13. December 2022

adds basic and modular logic stuff

Author:
Nilusink
"""
import pygame as pg
import typing as tp
from random import randint

from ..basegame.groups import Gates
from ..basegame.game import BaseGame
from ...additional.classes import Vec2
from .interactions import LinePoint, DraggablePoint


class Base(DraggablePoint):
    """
    basic logic element
    """
    _size: Vec2
    port_size: float = 10

    def __init__(self, position: Vec2, name: str, logic_func: tp.Callable, inputs: int, outputs: int):
        self.__id = Gates.yield_unique_id()

        self._input_points = []
        self._output_points = []

        self._size = Vec2.from_cartesian(100, self.port_size * ((max(inputs, outputs) + 1) * 2))

        self._name = name
        self._inputs = inputs
        self._outputs = outputs
        self._logic_func = logic_func

        super().__init__(position)
        Gates.add(self)

        # setup ports
        for i in range(inputs):
            off = self._size.y / (inputs * 2)
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

        for i in range(outputs):
            off = self._size.y / (outputs * 2)
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
    def id(self) -> int:
        """
        the gates unique id
        """
        return self.__id

    def draw(self, surface: pg.Surface):
        """
        draws the gate
        """
        # print(self.position.xy)
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

    def check_collision(self, point: Vec2):
        """
        check if the point is inside the hit-box
        """
        x = self.position.x - self._size.x / 2 <= point.x <= self.position.x + self._size.x / 2
        y = self.position.y - self._size.y / 2 <= point.y <= self.position.y + self._size.y / 2

        return x and y

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

    def __call__(self, *args, **kwargs):
        return self._logic_func(*args, **kwargs)


class And(Base):
    def __init__(self, position: Vec2):
        super().__init__(position, "And", lambda x, y: x and y, 2, 1)


class Not(Base):
    def __init__(self, position: Vec2):
        super().__init__(position, "Not", lambda x: not x, 1, 1)

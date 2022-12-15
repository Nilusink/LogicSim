"""
interactions.py
14. December 2022

A few GUI classes that have nothing to do with logic

Author:
Nilusink
"""
import pygame as pg

from ..basegame.groups import Drawn
from ..basegame.game import BaseGame
from ...additional.classes import Vec2


class DraggablePoint(pg.sprite.Sprite):
    _pos: Vec2
    radius: float
    color: tuple[float, float, float, float]
    _live_follow: bool = False

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

        # initialize pygame stuff
        super().__init__()
        Drawn.add(self)

        # create hooks
        BaseGame.on_event(pg.MOUSEBUTTONDOWN, self.start_follow)
        BaseGame.on_event(pg.MOUSEBUTTONUP, self.stop_follow)

    def draw(self, surface: pg.Surface):
        """
        how the point should be represented
        """
        if self._live_follow:
            self.position = pg.mouse.get_pos()

        pg.draw.circle(
            surface,
            self.color,
            self.position.xy,
            self.radius
        )

    def start_follow(self, event):
        """
        start the following of the mouse cursor
        """
        if event.button == 1:
            mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())
            delta = self.position - mouse_pos

            if delta.length <= self.radius:
                self._live_follow = True

    def stop_follow(self, event):
        """
        stop the following of the mouse cursor
        """
        if event.button == 1:
            self._live_follow = False

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

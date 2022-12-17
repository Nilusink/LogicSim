"""
lines.py
13. December 2022

The Basic Connection Line

Author:
Nilusink
"""
import typing as tp
from contextlib import suppress

import pygame as pg
from ..basegame.game import BaseGame
from ...additional.classes import Vec2
from ..basegame.groups import Drawn, Wires
from ...additional.functions import create_bezier


def aa_line(surface: pg.Surface, color: tuple[float, float, float], start_pos: tp.Any, end_pos: tp.Any, width: int = 1):
    """
    anti-aliased line
    """
    # big back line
    pg.draw.line(surface, color + (100,), start_pos, end_pos, width + 2)

    # main line
    pg.draw.line(surface, color + (255,), start_pos, end_pos, width)


class Line(pg.sprite.Sprite):
    set_points: list[Vec2] = ...
    _finished: bool = False
    _active: bool = False

    def __init__(self, start_pos: Vec2, parent):
        """
        set the first point and bind to mouse
        :param start_pos: the starting position of the line
        """
        self._parent = parent
        self._target = None
        self.set_points = [start_pos]

        super().__init__()
        self._id = Wires.yield_unique_id()
        Wires.add(self)
        Drawn.add(self)

        self.__hook_id = BaseGame.on_event(pg.MOUSEBUTTONDOWN, self.add_current_mouse)

    @property
    def id(self) -> int:
        return self._id

    @property
    def parent(self):
        return self._parent

    @property
    def target(self):
        return self._target

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool):
        self._active = value

        if self.target is not None:
            self.target.update_input(value)

    def set_target(self, target):
        """
        set the target node
        """
        print("updating target", target)
        self._target = target

    def set_parent(self, parent):
        print("updating parent", parent)
        self._parent = parent

    def draw(self, _surface: pg.Surface):
        """
        draw the current line
        """
        if pg.key.get_pressed()[pg.K_ESCAPE] and not self._finished:
            self.cancel()

        calc_points = self.set_points.copy()

        if not self._finished:
            # if shift is held, draw a straight line
            mouse_pos = pg.mouse.get_pos()
            mouse_pos = Vec2.from_cartesian(*mouse_pos)

            if pg.key.get_mods() & pg.KMOD_SHIFT:
                last_point = calc_points[-1]
                delta = last_point - mouse_pos

                if abs(delta.x) > abs(delta.y):
                    calc_points.append(Vec2.from_cartesian(mouse_pos.x, last_point.y))

                else:
                    calc_points.append(Vec2.from_cartesian(last_point.x, mouse_pos.y))

            else:
                calc_points.append(mouse_pos)

        # draw lines
        for i in range(len(calc_points) - 2):
            de1 = calc_points[i+1] - calc_points[i]
            de2 = calc_points[i+2] - calc_points[i+1]

            p1 = calc_points[i] + de1 * .8
            p2 = calc_points[i+1] + de2 * .2

            # create curves for the edges
            curve = create_bezier(p1, p2, calc_points[i+1])
            for j in range(len(curve) - 1):
                aa_line(
                    BaseGame.lowest_layer,
                    (255, 0, 0) if self.active else (50, 0, 0),
                    curve[j].xy, curve[j+1].xy,
                    width=3,
                )

            # draw straights
            aa_line(
                BaseGame.lowest_layer,
                color=(255, 0, 0) if self.active else (50, 0, 0),
                start_pos=(calc_points[i+1]-de1 * .8).xy if i != 0 else calc_points[0].xy,
                end_pos=p1.xy,
                width=3,
            )

        if len(calc_points) > 1:
            de2 = calc_points[-1] - calc_points[-2]

            p2 = calc_points[-2] + de2 * .2

            aa_line(
                BaseGame.lowest_layer,
                color=(255, 0, 0) if self.active else (50, 0, 0),
                start_pos=p2.xy if len(calc_points) != 2 else calc_points[0].xy,
                end_pos=calc_points[-1].xy,
                width=3,
            )

    def add_current_mouse(self, event: pg.event.Event):
        """
        add the current mouse position to the list
        """
        if event.button == 1:
            mouse_pos = Vec2.from_cartesian(*pg.mouse.get_pos())
            if pg.key.get_mods() & pg.KMOD_SHIFT:
                last_point = self.set_points[-1]
                delta = last_point - mouse_pos

                if abs(delta.x) > abs(delta.y):
                    self.add(Vec2.from_cartesian(mouse_pos.x, last_point.y))

                else:
                    self.add(Vec2.from_cartesian(last_point.x, mouse_pos.y))

            else:
                self.add(mouse_pos)

    def add(self, point: Vec2):
        """
        add a point to the line
        """
        self.set_points.append(point)

    def cancel(self):
        """
        stop drawing the line and delete it
        """
        if BaseGame.globals.drawing_line is self:
            BaseGame.globals.drawing_line = None

        Drawn.remove(self)

        self.set_points.clear()

        self.finish()
        del self

    def delete(self):
        """
        does the same as cancel, for compatability
        """
        self.cancel()

    def finish(self):
        """
        stop drawing the line
        """
        with suppress(KeyError):
            BaseGame.clear_on_event(self.__hook_id)
        self._finished = True

    def __repr__(self) -> str:
        return f"<Line {self.id}>"

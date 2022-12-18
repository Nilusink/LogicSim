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
    hover_thickness: int = 10
    thickness: int = 5

    _max_curve_distance: int = 20
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

    def check_collision(self, position: Vec2, collision_range: int = 10, accuracy: int = 100) -> bool:
        """
        checks if the given point is within the lines hit-box
        """
        return False

        # first check if the point is even in the box of the line
        all_x = [pnt.x for pnt in self.set_points]
        all_y = [pnt.y for pnt in self.set_points]

        min_pnt = Vec2.from_cartesian(min(all_x), min(all_y))
        max_pnt = Vec2.from_cartesian(max(all_x), max(all_y))

        if not (
                min_pnt.x <= position.x <= max_pnt.x,
                min_pnt.y <= position.y <= max_pnt.y,
        ):
            return False

        # more accurately check
        for i in range(len(self.set_points) - 1):
            pnt1 = self.set_points[i]
            pnt2 = self.set_points[i+1]

            delta = pnt2 - pnt1

            # for each line, dissect it into `accuracy` amount of points and check at each point if the position is
            # within `collision_range` pixels
            for j in range(accuracy):
                perc = j / accuracy

                probe_point = pnt1 + delta * perc
                distance = position - probe_point

                if distance.length <= collision_range:
                    return True

        return False

    def set_target(self, target):
        """
        set the target node
        """
        self._target = target

    def set_parent(self, parent):
        self._parent = parent

    def draw(self, _surface: pg.Surface):
        """
        draw the current line
        """
        if self.parent is not None and "c" in self.parent.id:
            return

        if self.target is not None and "c" in self.target.id:
            return

        if pg.key.get_pressed()[pg.K_ESCAPE] and not self._finished:
            self.cancel()

        mouse_pos = pg.mouse.get_pos()
        mouse_pos = Vec2.from_cartesian(*mouse_pos)

        hover = False
        if self._finished:
            hover = self.check_collision(mouse_pos) and BaseGame.globals.drawing_line is None

        calc_points = self.set_points.copy()

        if not self._finished:
            # if shift is held, draw a straight line
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
            # calculate the curve offset points
            de1 = calc_points[i+1] - calc_points[i]
            de2 = calc_points[i+2] - calc_points[i+1]

            off1 = de1 * .8
            off11 = (de1.length - self._max_curve_distance)
            off2 = de2 * .2

            # either 20% or a max of `self._max_curve_distance`
            off1.length = off1.length if off11 < off1.length else off11
            off2.length = off2.length if self._max_curve_distance > off2.length else self._max_curve_distance

            p1 = calc_points[i] + off1
            p2 = calc_points[i+1] + off2

            # create curves for the edges
            curve = create_bezier(p1, p2, calc_points[i+1], resolution=10)
            for j in range(len(curve) - 1):
                aa_line(
                    BaseGame.lowest_layer,
                    (255, 0, 0) if self.active else (50, 0, 0),
                    curve[j].xy, curve[j+1].xy,
                    width=self.hover_thickness if hover else self.thickness,
                )

            # draw straights
            aa_line(
                BaseGame.lowest_layer,
                color=(255, 0, 0) if self.active else (50, 0, 0),
                start_pos=(calc_points[i+1]-off1).xy if i != 0 else calc_points[0].xy,
                end_pos=p1.xy,
                width=self.hover_thickness if hover else self.thickness,
            )

        if len(calc_points) > 1:
            de2 = calc_points[-1] - calc_points[-2]

            off = de2 * .2
            off.length = off.length if off.length < self._max_curve_distance else self._max_curve_distance

            p2 = calc_points[-2] + off

            aa_line(
                BaseGame.lowest_layer,
                color=(255, 0, 0) if self.active else (50, 0, 0),
                start_pos=p2.xy if len(calc_points) != 2 else calc_points[0].xy,
                end_pos=calc_points[-1].xy,
                width=self.hover_thickness if hover else self.thickness,
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

        elif event.button == 3:
            self.delete()

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

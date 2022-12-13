"""
lines.py
13. December 2022

The Basic Connection Line

Author:
Nilusink
"""
import pygame as pg
from ..basegame.groups import Drawn
from ..basegame.game import BaseGame
from ...additional.classes import Vec2
from ...additional.functions import create_bezier


class Line(pg.sprite.Sprite):
    set_points: list[Vec2] = ...
    _finished: bool = False
    active: bool = False

    def __init__(self, start_pos: Vec2):
        """
        set the first point and bind to mouse
        :param start_pos: the starting position of the line
        """
        self.set_points = [start_pos]

        super().__init__()
        Drawn.add(self)

        self.__hook_id = BaseGame.on_event(pg.MOUSEBUTTONDOWN, self.add_current_mouse)

    def draw(self, surface: pg.Surface):
        """
        draw the current line
        """
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

        for i in range(len(calc_points) - 2):
            de1 = calc_points[i+1] - calc_points[i]
            de2 = calc_points[i+2] - calc_points[i+1]

            p1 = calc_points[i] + de1 * .8
            p2 = calc_points[i+1] + de2 * .2

            curve = create_bezier(p1, p2, calc_points[i+1])
            for j in range(len(curve) - 1):
                pg.draw.line(
                    surface,
                    (255, 0, 0, 255) if self.active else (50, 0, 0, 255),
                    curve[j].xy, curve[j+1].xy,
                    width=3,
                )

            pg.draw.line(
                surface,
                color=(255, 0, 0, 255) if self.active else (50, 0, 0, 255),
                start_pos=(calc_points[i+1]-de1 * .8).xy,
                end_pos=p1.xy,
                width=3,
            )

        de2 = calc_points[-1] - calc_points[-2]

        p2 = calc_points[-2] + de2 * .2

        pg.draw.line(
            surface,
            color=(255, 0, 0, 255) if self.active else (50, 0, 0, 255),
            start_pos=p2.xy,
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

        elif event.button == 3:
            self.finish()

    def add(self, point: Vec2):
        """
        add a point to the line
        """
        self.set_points.append(point)

    def finish(self):
        """
        stop drawing the line
        """
        BaseGame.clear_on_event(self.__hook_id)
        self._finished = True

"""
curves.py
13. December 2022

a few tests

Author:
Nilusink
"""
import pygame as pg
from time import sleep

from sim.core.basegame import BaseGame
# from sim.core.drawables.lines import Line
from sim.core.drawables.interactions import DraggablePoint

from sim.additional.classes import Vec2

from sim.additional.functions import animated_4bezier, create_bezier


def main():
    """
    runs the game
    """
    # Line(Vec2.from_cartesian(0, 0))

    p1p = Vec2.from_cartesian(150, 50)
    p2p = Vec2.from_cartesian(700, 500)
    p3p = Vec2.from_cartesian(50, 500)
    p4p = Vec2.from_cartesian(600, 100)

    p1 = DraggablePoint(p1p)
    p2 = DraggablePoint(p2p)
    p3 = DraggablePoint(p3p)
    p4 = DraggablePoint(p4p)

    res = 200

    while True:
        for i in range(res):
            curve = animated_4bezier(p1.position, p2.position, p3.position, p4.position, res, i)

            for j in range(i):
                BaseGame.in_loop(
                    pg.draw.line,
                    BaseGame.lowest_layer,
                    (255, 255, 255, 255),
                    curve[j].xy,
                    curve[j+1].xy,
                    width=5
                )

            sleep(.01)

            BaseGame.update()


if __name__ == '__main__':
    main()

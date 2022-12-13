"""
main.py
13. December 2022

main file game

Author:
Nilusink
"""
import pygame as pg
from sim.core.basegame import BaseGame
from sim.core.drawables.lines import Line

from sim.additional.classes import Vec2

from sim.additional.functions import animated_bezier, create_bezier


def main():
    """
    runs the game
    """
    Line(Vec2.from_cartesian(0, 0))

    # p1 = Vec2.from_cartesian(150, 50)
    # p2 = Vec2.from_cartesian(600, 300)
    # p3 = Vec2.from_cartesian(300, 500)

    while True:
        # animated_bezier(p1, p3, p2)
        BaseGame.update()


if __name__ == '__main__':
    main()

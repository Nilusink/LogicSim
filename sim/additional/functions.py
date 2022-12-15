"""
functions.py
13. December 2022

useful functions

Author:
Nilusink
"""
from time import sleep

from .classes import Vec2
from ..core.basegame.game import BaseGame, pg


def create_bezier(start: Vec2, end: Vec2, top: Vec2, resolution: int = 20) -> list[Vec2]:
    """
    create a beautiful Bézier curve from start end and top poit
    """
    g1 = top - start
    g2 = end - top

    points: list[Vec2] = []

    for i in range(resolution):
        i /= resolution

        p1 = start + g1 * i
        p2 = top + g2 * i

        g3 = p2 - p1
        p3 = p1 + g3 * i

        points.append(p3)

    points.append(end)
    return points


def animated_bezier(start: Vec2, end: Vec2, top: Vec2, resolution: int = 200) -> list[Vec2]:
    """
    create a beautiful Bézier curve from start end and top poit
    """
    g1 = top - start
    g2 = end - top

    points: list[Vec2] = []

    for i in range(resolution):
        i /= resolution

        p1 = start + g1 * i
        p2 = top + g2 * i

        g3 = p2 - p1
        p3 = p1 + g3 * i

        BaseGame.middle_layer.fill((0, 0, 0, 255))

        pg.draw.line(BaseGame.middle_layer, (255, 0, 0, 255), start.xy, top.xy)
        pg.draw.line(BaseGame.middle_layer, (255, 0, 0, 255), top.xy, end.xy)
        pg.draw.line(BaseGame.middle_layer, (255, 255, 0, 255), p1.xy, p2.xy)

        pg.draw.circle(BaseGame.middle_layer, (255, 255, 255, 255), p1.xy, 5)
        pg.draw.circle(BaseGame.middle_layer, (255, 255, 255, 255), p2.xy, 5)
        pg.draw.circle(BaseGame.middle_layer, (255, 0, 255, 255), p3.xy, 5)

        pg.draw.circle(BaseGame.middle_layer, (100, 100, 100, 255), start.xy, 5)
        pg.draw.circle(BaseGame.middle_layer, (100, 100, 100, 255), end.xy, 5)
        pg.draw.circle(BaseGame.middle_layer, (100, 100, 100, 255), top.xy, 5)

        points.append(p3)

        for j in range(len(points) - 1):
            pg.draw.line(BaseGame.middle_layer, (255, 0, 255, 255), points[j].xy, points[j+1].xy)

        # BaseGame.update()
        # pg.display.update()
        BaseGame.screen.blit(BaseGame.middle_layer, (0, 0))
        pg.display.update()
        sleep(.01)

    points.append(end)
    return points


def animated_4bezier(
        pnt1: Vec2,
        pnt2: Vec2,
        pnt3: Vec2,
        pnt4: Vec2,
        resolution: int = 200,
        draw: int = -1
) -> list[Vec2]:
    """
    create a beautiful Bézier curve from start end and top poit
    """
    g1 = pnt2 - pnt1
    g2 = pnt3 - pnt2
    g3 = pnt4 - pnt3

    points: list[Vec2] = []

    for i in range(resolution):
        t = i / resolution

        p1 = pnt1 + g1 * t
        p2 = pnt2 + g2 * t
        p3 = pnt3 + g3 * t

        g4 = p2 - p1
        g5 = p3 - p2

        p4 = p1 + g4 * t
        p5 = p2 + g5 * t

        g6 = p5 - p4

        p6 = p4 + g6 * t

        if draw == i:
            BaseGame.in_loop(pg.draw.line, BaseGame.middle_layer, (255, 0, 0, 100), pnt1.xy, pnt2.xy)
            BaseGame.in_loop(pg.draw.line, BaseGame.middle_layer, (255, 0, 0, 100), pnt2.xy, pnt3.xy)
            BaseGame.in_loop(pg.draw.line, BaseGame.middle_layer, (255, 0, 0, 100), pnt3.xy, pnt4.xy)
            BaseGame.in_loop(pg.draw.line, BaseGame.middle_layer, (255, 255, 0, 200), p1.xy, p2.xy)
            BaseGame.in_loop(pg.draw.line, BaseGame.middle_layer, (255, 255, 0, 200), p2.xy, p3.xy)
            BaseGame.in_loop(pg.draw.line, BaseGame.middle_layer, (255, 0, 255, 200), p4.xy, p5.xy)

            BaseGame.in_loop(pg.draw.circle, BaseGame.middle_layer, (255, 255, 0, 127), p1.xy, 5)
            BaseGame.in_loop(pg.draw.circle, BaseGame.middle_layer, (255, 255, 0, 127), p2.xy, 5)
            BaseGame.in_loop(pg.draw.circle, BaseGame.middle_layer, (255, 255, 0, 127), p3.xy, 5)
            BaseGame.in_loop(pg.draw.circle, BaseGame.middle_layer, (255, 0, 255, 127), p4.xy, 5)
            BaseGame.in_loop(pg.draw.circle, BaseGame.middle_layer, (255, 0, 255, 127), p5.xy, 5)
            BaseGame.in_loop(pg.draw.circle, BaseGame.middle_layer, (255, 255, 255, 127), p6.xy, 5)

            # BaseGame.in_loop(pg.draw.circle, BaseGame.middle_layer, (100, 100, 100, 127), pnt1.xy, 5)
            # BaseGame.in_loop(pg.draw.circle, BaseGame.middle_layer, (100, 100, 100, 127), pnt2.xy, 5)
            # BaseGame.in_loop(pg.draw.circle, BaseGame.middle_layer, (100, 100, 100, 127), pnt3.xy, 5)
            # BaseGame.in_loop(pg.draw.circle, BaseGame.middle_layer, (100, 100, 100, 127), pnt4.xy, 5)

        points.append(p6)

    points.append(pnt4)
    return points

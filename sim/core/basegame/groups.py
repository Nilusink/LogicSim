"""
groups.py
13. December 2022

Defines all Sprite Groups

Author:
Nilusink
"""
import pygame as pg


class _Blocks(pg.sprite.Group):
    ...


class _Drawn(pg.sprite.Group):
    """
    members need:

    functions:

    - draw(surface: pg.Surface)
    """

    def draw(self, surface: pg.Surface):
        for sprite in self.sprites():
            sprite.draw(surface)


# Instances
Drawn = _Drawn()
Blocks = _Blocks()

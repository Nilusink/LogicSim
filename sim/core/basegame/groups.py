"""
groups.py
13. December 2022

Defines all Sprite Groups

Author:
Nilusink
"""
import pygame as pg


class _Updated(pg.sprite.Group):
    """
    members need:

    functions:

    - update(delta: float)
    """
    def update(self, delta: float):
        for sprite in self.sprites():
            sprite.update(delta)


class _Drawn(pg.sprite.Group):
    """
    members need:

    functions:

    - draw(surface: pg.Surface)
    """

    def draw(self, surface: pg.Surface):
        for sprite in self.sprites():
            sprite.draw(surface)


class _Gates(pg.sprite.Group):
    """
    members need:

    properties:

    - id: int
    """
    def get_by_id(self, id: int):
        for sprite in self.sprites():
            if sprite.id == id:
                return sprite

    def id_taken(self, id: int) -> bool:
        for sprite in self.sprites():
            if sprite.id == id:
                return True

        return False

    def yield_unique_id(self) -> int:
        """
        yields a valid unique id
        """
        if len(self.sprites()) == 0:
            return 0

        return max([sprite.id for sprite in self.sprites()]) + 1


class _Wires(_Gates):
    ...


# Instances
Drawn = _Drawn()
Gates = _Gates()
Wires = _Wires()
Updated = _Updated()

"""
game.py
13. December 2022

Pygame backbone

Author:
Nilusink
"""
from random import randint
import pygame as pg
import typing as tp


# local imports
from ...additional.classes import BetterDict
from .groups import Drawn


# Constants
DEFAULT_WINDOW_SIZE: tuple[int, int] = (1000, 600)


class Hook(tp.TypedDict):
    event: pg.event.Event
    func: tp.Callable


class _BaseGame:
    running: bool = True
    _hooks: dict[int, Hook]

    def __init__(self):
        """
        Initialize the game on the lowest level
        """
        window_size = DEFAULT_WINDOW_SIZE
        self._hooks = {}

        # initialize pygame
        pg.init()
        pg.font.init()

        # create screens and layers
        self.screen = pg.display.set_mode(window_size, pg.SCALED)
        self.lowest_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.middle_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.top_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.font = pg.font.SysFont(None, 24)
        pg.display.set_caption("Digital Logic Sim")

    def update(self):
        """
        update the whole game
        """
        self._handle_events()

        # clear screens
        self.screen.fill((50, 50, 50, 0))
        self.lowest_layer.fill((0, 0, 0, 0))
        self.middle_layer.fill((0, 0, 0, 0))
        self.top_layer.fill((0, 0, 0, 0))

        Drawn.draw(self.middle_layer)

        # draw layers
        self.screen.blit(self.lowest_layer, (0, 0))
        self.screen.blit(self.middle_layer, (0, 0))
        self.screen.blit(self.top_layer, (0, 0))

        pg.display.update()

    def _handle_events(self):
        """
        handle pygame events
        """
        # base events
        events = pg.event.get()
        for event in events:
            match event.type:
                case pg.QUIT:
                    self.exit()

        # hooks
        for hid in self._hooks.copy():
            try:
                for event in events:
                    if event.type == self._hooks[hid]["event"]:
                        self._hooks[hid]["func"](event)

            except KeyError:
                continue

    def on_event(self, event: pg.event.Event, func: tp.Callable) -> int:
        """
        bind a function to the event

        :param event:
        :param func:
        :returns: the id to cancel the event
        """
        pid = 100_000
        while pid in self._hooks:
            pid = randint(100_001, 999_999)

        self._hooks[pid] = {
            "event": event,
            "func": func,
        }

        return pid

    def clear_on_event(self, hook_id: int):
        """
        clear a previously scheduled hook
        :param hook_id: the id returned
        """
        self._hooks.pop(hook_id)

    def exit(self):
        """
        close the game
        """
        self.running = False
        quit(0)


BaseGame = _BaseGame()

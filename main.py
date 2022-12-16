"""
main.py
13. December 2022

main file game

Author:
Nilusink
"""
from sim.core.drawables.interactions import Button
from sim.core.drawables.interactions import InputsBox, OutputsBox
from sim.core.drawables.logic import Not, And
from sim.core.basegame.game import BaseGame
from sim.additional.classes import Vec2


def main():
    """
    main program
    """
    def spawn_and(*_trash):
        ad = And(Vec2())
        ad.start_follow()

    def spawn_not(*_trash):
        ad = Not(Vec2())
        ad.start_follow()

    Button(
        (0, 1000),
        (200, 80),
        text="And",
        on_click=spawn_and,
    )
    Button(
        (201, 1000),
        (200, 80),
        text="Not",
        on_click=spawn_not,
    )

    InputsBox(
        (50, 100),
        (50, 800),
    )

    OutputsBox(
        (1820, 100),
        (50, 800),
    )

    while True:
        BaseGame.update()


if __name__ == '__main__':
    main()

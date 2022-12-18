"""
main.py
13. December 2022

main game file

Author:
Nilusink
"""
from traceback import format_exc
from random import  randint
import pygame as pg
import os

from sim.core.drawables.interactions import InputsBox, OutputsBox
from sim.core.drawables.logic import Not, And, Base, CustomBlock
from sim.core.serialize import serialize_all, load_from_file
from sim.core.drawables.interactions import Button, Entry
from sim.core.basegame.groups import Gates, Wires
from sim.core.basegame.game import BaseGame
from sim.core.drawables.lines import Line
from sim.additional.classes import Vec2


def main():
    """
    main program
    """
    inputs = InputsBox(
        (50, 100),
        (50, 800),
    )

    outputs = OutputsBox(
        (1820, 100),
        (50, 800),
    )

    def spawn_and(*_trash):
        ad = And(Vec2())
        ad.start_follow()

    def spawn_not(*_trash):
        ad = Not(Vec2())
        ad.start_follow()

    def generate_block(*_trash):
        try:
            block_name = name.text
            name.text = f"Block {randint(100_000, 999_999)}"

            inp = inputs.inputs
            out = outputs.inputs

            if not (inp and out):
                return

            # write to file
            serialize_all(f"./blocks/{block_name}.json")

            # create new block from old gates
            new_block = CustomBlock(
                (0, 0),
                block_name,
                None,
                len(inp),
                len(out),
            )

            # move old gates
            gates: list[Base] = Gates.sprites()
            wires: list[Line] = Wires.sprites()

            # remove all points that are not connected to a gate (first and last)
            for wire in wires:
                wire.set_points = [wire.set_points[0], wire.set_points[-1]]

            # move inputs to block input
            for i in range(len(inputs.inputs)):
                for wire in inputs.inputs[i].lb.connected_lines:
                    wire.set_parent(new_block.input_output_points[i])
                    new_block.input_output_points[i].add_connection(wire)

            # move outputs to block output
            for i in range(len(outputs.inputs)):
                for wire in outputs.inputs[i].lb.connected_lines:
                    wire.set_target(new_block.output_input_points[i])
                    new_block.output_input_points[i].add_connection(wire)

            # move all gates out of the screen
            for gate in gates:
                gate.position = (1000, -10_000)

            # remove all inputs and outputs
            inputs.clear()
            outputs.clear()

            new_block.start_follow()

            blocks_buttons.append(
                Button(
                    (201 * (len(blocks_buttons) + 2), 1000),
                    (200, 80),
                    text=block_name,
                    on_click=lambda *_e, f=f"./blocks/{block_name}.json": load_previous(f),
                    bg=(100, 200, 100, 255),
                    active_bg=(150, 200, 150, 255),
                )
            )

        except Exception as e:
            print("error:", format_exc())
            raise e

    def load_previous(file: str, load_as_block: bool = False):

        if not os.path.exists(file):
            return

        load_from_file(file, load_as_block)
        if not load_as_block:
            name.text = ".".join(file.split("/")[-1].split("\\")[-1].split(".")[:-1])

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

    Button(
        (0, 0),
        (200, 80),
        text="Create",
        on_click=generate_block,
        bg=(100, 100, 200, 255),
        active_bg=(150, 150, 200, 255),
    )

    Button(
        (201, 0),
        (200, 80),
        text="Exit",
        on_click=lambda *_e: pg.quit(),
    )

    i = 1
    blocks_buttons: list[Button] = []
    for file in os.listdir("./blocks"):
        i += 1
        blocks_buttons.append(Button(
            (201 * i, 1000),
            (200, 80),
            text=".".join(file.split(".")[:-1]),
            on_click=lambda *_e, f=f"./blocks/{file}": load_previous(f),
            bg=(100, 200, 100, 255),
            active_bg=(150, 200, 150, 255),
        ))

    name = Entry(
        (760, 5),
        (400, 80),
        bg=(60, 60, 60, 150),
        active_bg=(70, 70, 70, 230),
        border_radius=20,
    )
    name.text = f"Block {randint(100_000, 999_999)}"

    while True:
        BaseGame.update()


if __name__ == '__main__':
    main()

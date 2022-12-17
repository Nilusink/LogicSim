"""
main.py
13. December 2022

main file game

Author:
Nilusink
"""
from traceback import format_exc
import base64
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
            name.text = f"Block {base64.b64encode(os.urandom(3)).decode()}"

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

            for button in blocks_buttons:
                button.delete()

            i = 1
            for file in os.listdir("./blocks"):
                i += 1
                blocks_buttons.append(
                    Button(
                        (201 * i, 1000),
                        (200, 80),
                        text=".".join(file.split(".")[:-1]),
                        on_click=lambda *_e, f=f"./blocks/{file}": load_prevoius(f),
                        bg=(100, 200, 100, 255),
                        active_bg=(150, 200, 150, 255),
                    )
                )

        except Exception as e:
            print("error:", format_exc())
            raise e

    def load_prevoius(file: str):
        if not os.path.exists(file):
            return

        load_from_file(file, True)

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

    i = 1
    blocks_buttons: list[Button] = []
    for file in os.listdir("./blocks"):
        i += 1
        blocks_buttons.append(Button(
            (201 * i, 1000),
            (200, 80),
            text=".".join(file.split(".")[:-1]),
            on_click=lambda *_e, f=f"./blocks/{file}": load_prevoius(f),
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
    name.text = f"Block {base64.b64encode(os.urandom(3)).decode()}"

    while True:
        BaseGame.update()


if __name__ == '__main__':
    main()

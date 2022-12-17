"""
serialize.py
17. December 2022

for saving the game

Author:
Nilusink
"""
import typing as tp
import pickle
import json

# local imports
from .drawables.interactions import InputsBox, LinePoint, OutputsBox
from .drawables.logic import And, Not, Base
from .basegame.groups import Gates, Wires
from ..additional.classes import Vec2
from .drawables.lines import Line
from .drawables.logic import Base


class GateType(tp.TypedDict):
    position: tuple[int | float, int | float]
    args: tuple
    type: str
    id: int


class WireType(tp.TypedDict):
    parent: str
    target: str
    points: list[tuple[int | float, int | float]]


class SerializedOutput(tp.TypedDict):
    input: list[int | float]
    output: list[int | float]
    gates: list[GateType]
    wires: list[WireType]


def serialize_args(arguments: tuple) -> tuple:
    """
    convert non JSON-serizable arguments to valid JSON arguments
    """
    out: list[tp.Any] = []
    for arg in arguments:
        arg: tp.Any

        if issubclass(type(arg), Vec2):
            arg: Vec2
            out.append(arg.xy)

        elif issubclass(type(arg), tp.Callable):
            arg: tp.Callable
            encoded_func = str(pickle.dumps(arg))
            out.append(encoded_func)

        else:
            out.append(arg)

    return tuple(out)


def serialize_all(file: str):
    """
    save a thing
    """
    inputs: list[int | float] = [input.cb.position.y for input in InputsBox.instance.inputs]
    outputs: list[int | float] = [input.cb.position.y for input in OutputsBox.instance.inputs]

    out: SerializedOutput = {
        "input": inputs,
        "output": outputs,
        "gates": [],
        "wires": [],
    }

    gates: list[Base] = Gates.sprites()
    wires: list[Line] = Wires.sprites()

    for gate in gates:
        out["gates"].append({
            "position": gate.position.xy,
            "args": serialize_args(gate.initial_args),
            "type": gate.__class__.__name__,
            "id": gate.id,
        })

    for wire in wires:
        pid: str = wire.parent.id
        tid: str = wire.target.id

        out["wires"].append({
            "parent": pid,
            "target": tid,
            "points": [point.xy for point in wire.set_points],
        })

    with open(file, "w") as outfile:
        json.dump(out, outfile, indent=4)


def load_from_file(file: str, load_as_block: bool = False):
    """
    load a saved thing
    """

    data: SerializedOutput = json.load(open(file, "r"))

    if not load_as_block:
        # clear current screen
        for gate in Gates.sprites():
            gate.delete()

        for wire in Wires.sprites():
            wire.delete()

        # create input and output ports
        for i_y in data["input"]:
            InputsBox.instance.add_input(i_y)

        for o_y in data["output"]:
            OutputsBox.instance.add_input(o_y)

    # for correctly wiring the wires
    gate_alias: dict[int, Base] = {}

    # create gates
    for gate in data["gates"]:
        match gate["type"]:
            case "And":
                new_gate = And(*gate["args"])

            case "Not":
                new_gate = Not(*gate["args"])

            case _:
                continue

        new_gate.position = gate["position"]
        gate_alias[gate["id"]] = new_gate

    # connect wires
    for wire in data["wires"]:
        pid = wire["parent"]
        tid = wire["target"]

        # check if the point is valid
        if "i" in pid:
            raise RuntimeError("parent node can only be of type output")

        if "o" in tid:
            raise RuntimeError("target node can only be of type input")

        # split the ids into useful data
        parent, pid = pid.split("o")
        target, tid = tid.split("i")

        # convert to integer values
        parent, pid = int(parent), int(pid)
        target, tid = int(target), int(tid)

        parent_node: LinePoint
        target_node: LinePoint

        # get the parent node
        if parent >= 0:
            parent = gate_alias[parent]
            parent_node = parent.output_points[pid]

        elif parent == -1:
            parent = InputsBox.instance
            parent_node = parent.inputs[pid].lb

        elif parent == -2:
            raise RuntimeError("parent cannot be output node")

        else:
            raise RuntimeError("invalid parent node id")

        # get the target node
        if target >= 0:
            target = gate_alias[target]
            target_node = target.input_points[tid]

        elif target == -1:
            raise RuntimeError("target cannot be input node")

        elif target == -2:
            target = OutputsBox.instance
            target_node = target.inputs[tid].lb

        else:
            raise RuntimeError("invalid target node id")

        # create new line
        new_line = Line(
            start_pos=parent_node.position,
            parent=parent_node,
        )

        # add all points to line
        for point in wire["points"][1:-1]:
            new_line.add(Vec2.from_cartesian(*point))

        # add target node
        new_line.add(target_node.position)
        new_line.finish()
        new_line.set_target(target_node)

        # notify parents about the newly created child that belongs to them
        parent_node.add_connection(new_line)
        target_node.add_connection(new_line)

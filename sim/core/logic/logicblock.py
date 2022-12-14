"""
logicblock.py
14. December 2022

Base implementation of a logic block that doesn't do anything 
by itself.

Author:
melektron
"""

from blockio import BlockOutput


class LogicBlock:
    _inputs: list[BlockOutput]

    def __init__(self, inputs: list[BlockOutput]) -> None:
        self._inputs = inputs
        pass

    def compute(self):
        print(f"input values: {[blinput.value for blinput in self._inputs]}")
        pass

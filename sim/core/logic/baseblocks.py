"""
baseblocks.py
14. December 2022

The most basic logic blocks all other logic blocks
are constructed out of.

Author:
melektron
"""

from logicblock import LogicBlock
from blockio import BlockOutput
from logicexcept import InputError


class AndBlock(LogicBlock):
    def __init__(self, inputs: list[BlockOutput]) -> None:
        if not len(inputs) == 2:
            raise InputError
        self._inputs = inputs
    
    def compute(self):
        return self._inputs[0].value and self._inputs[1].value
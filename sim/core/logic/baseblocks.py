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


class AndBlock(LogicBlock):
    def __init__(self, inputs: list[BlockOutput]) -> None:
        self._inputs = inputs
        pass
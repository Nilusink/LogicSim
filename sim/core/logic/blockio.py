"""
blockio.py
14. December 2022

Classes representing block inputs and outputs
and managing their connections.

Author:
melektron
"""


class BlockOutput:
    _output_value: bool
    label: str

    def __init__(self, label="", initial_value=False) -> None:
        self._output_value = initial_value
        self.label = label

    @property
    def value(self) -> bool:
        print(f"read output of block {self.label}")
        return self._output_value

    @value.setter
    def value(self, new_value: bool):
        print(f"update output of block {self.label}")
        self._output_value = new_value


class BlockInput:

    def __init__(self) -> None:
        pass

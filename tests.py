"""
tests.py
14. December 2022

Code to run tests without the UI.

Author:
melektron
"""

import sys

from .sim.core.logic.baseblocks import AndBlock
from .sim.core.logic.blockio import BlockOutput


def print_quick_help():
    print(
"""Usage: <command> <test name> [test parameters]
Available test names:
    - blockio"""
    )


def test_blockio() -> int:
    o1 = BlockOutput("output1", False)
    o2 = BlockOutput("output2", True)

    block1 = AndBlock([o1, o2])
    block2 = AndBlock([o2, o1])

    print(block1.compute())
    print(block2.compute())

    o1.value = True
    o2.value = True

    print(block1.compute())
    print(block2.compute())

    return 0


def main():
    ret: int = 0

    if len(sys.argv) < 2:
        print_quick_help()
        return 1

    match sys.argv[1]:
        case "blockio":
            ret = test_blockio()

    if ret != 0:
        print(f"ERROR: Test failed with code: {ret}")
        return ret

    print("OK: Test successful")
    return 0


if __name__ == "__main__":
    sys.exit(main())

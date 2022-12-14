"""
__main__.py
14. December 2022

Package main function to run simulation tests without 
the UI.

Author:
melektron
"""

import sys

from baseblocks import AndBlock
from blockio import BlockOutput


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

    block1.compute()
    block2.compute()

    o1.value = True
    o2.value = False

    block1.compute()
    block2.compute()

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

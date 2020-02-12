"""Battleships package entry module."""

import sys

import params
from battleships import puzzle


def run() -> None:
    """Run the puzzle solver.
    
    The results are written in the default output file whose path is
    defined in the params module.
    
    This function catches any previously uncaught exceptions (at least
    those derived from Exception base class) and sends the appropriate
    exit code to the OS.
    """

    if __name__ == "__main__":
        try:
            with open(params.OUTPUT_FILE_PATH, "w", encoding="utf-8") as ofile:
                puzzle.Puzzle.run(ofile)
        except Exception:  # pylint: disable=W0703
            sys.exit(params.FAILURE_EXIT_CODE)


run()

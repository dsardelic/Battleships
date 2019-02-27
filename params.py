"""This module contains application-wide used parameters and string
messages.
"""

import pathlib
import types


FAILURE_EXIT_CODE = 1

FIELDTYPE_SYMBOLS = types.SimpleNamespace()
FIELDTYPE_SYMBOLS.SEA = "."
FIELDTYPE_SYMBOLS.SHIP = "O"
FIELDTYPE_SYMBOLS.UNKNOWN = "x"

INPUT_FILE_NAME = "Battleships.in"
OUTPUT_FILE_NAME = "Battleships.out"
PROJECT_ROOT_PATH = pathlib.Path(__file__).resolve().parent
INPUT_FILE_PATH = PROJECT_ROOT_PATH.joinpath(INPUT_FILE_NAME)
OUTPUT_FILE_PATH = PROJECT_ROOT_PATH.joinpath(OUTPUT_FILE_NAME)

MESSAGES = types.SimpleNamespace()
MESSAGES.INVALID_INPUT_FILE_PATH = "Invalid input data file path."
MESSAGES.SOLUTIONS_FOUND = "{} solutions in total."
MESSAGES.NO_SOLUTIONS_FOUND = "No solutions found."

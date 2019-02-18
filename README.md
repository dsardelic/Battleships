# Battleships

## What is Battleships?

Battleships is a program for solving the popular [Battleship](https://en.wikipedia.org/wiki/Battleship_(puzzle)) puzzle.

## How does it work?

### INI file

The [INI file](Battleships.ini) specifies the following:

* Path to the input data file (absolute or relative with regard to the [battleships](battleships.py) module)
* Symbols used for marking a specific field type: sea, ship or unknown (i.e. undetermined).

While the values' symbols are arbitrary, the keys' names must be SHIP, SEA and UNKNOWN. These are also the only currently used and recognized field types.

### Input data file

The input data file is a text file with the following structure:

* Row 1 - Number (SHIP_TYPES) of used ship types, equivalent to count of distinct ship lengths.
* Rows 2 through (1 + SHIP_TYPES) - Two whitespace-separated numbers representing ship length/type and corresponding ship count respectively.
* Row (2 + SHIP_TYPES) - Board playfield size (BOARD_SIZE). The program currently handles square boards only.
* Row (3 + SHIP_TYPES) - BOARD_SIZE whitespace-separated numbers representing total number of ship pieces in each of the BOARD_SIZE board rows respectively.
* Row (4 + SHIP_TYPES) - BOARD_SIZE whitespace-separated numbers representing total number of ship pieces in each of the BOARD_SIZE board columns respectively.
* Rows (5 + SHIP_TYPES) through (4 + SHIP_TYPES + BOARD_SIZE) - String of BOARD_SIZE characters representing a field type in a particular board row and column. Each used character must be linked to the corresponding field type in the [INI file](Battleships.ini).

### How to run the program?

Battleships is a Python3 program. After setting the input data file location (and, if necessary, the field type symbols) in the [INI file](Battleships.ini), just run the [battleships](battleships.py) module. Solutions are printed to standard output.

## Can it be optimized?

Sure, in a number of ways, for instance by:

* Developing a GUI to collect input data and display solutions.
* Implementing input data format validation.
* Implementing additional field type handling, e.g. for fields representing a ship of length 1, a ship's bow or stern (including ship's orientation on the board) or an unspecified ship part.
* etc.

## May I use this program?

This program is licensed under the MIT license which can be found in a [separate file](LICENSE).

## How can I contact the author?

You can reach me by e-mail at sardinhoATgmail.com.

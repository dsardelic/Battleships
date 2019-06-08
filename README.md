# Battleships

## What is Battleships?

Battleships is a program for solving the popular [Battleship](https://en.wikipedia.org/wiki/Battleship_(puzzle)) puzzle.

## How does it work?

### Params module

The [params](params.py) module specifies the following:

* OS exit code in case of unsuccessful program termination. (e.g. 1)
* Symbols used for marking a specific field type: sea, ship or unknown/undetermined (e.g. ".", "O", and "x").
* Input and output file name (e.g. "Battleships.in" and "Battleships.out") and path. The default input and output file folder is the same folder where the [params](params.py) module is located (e.g. project root path).
* Output message strings (single language only, no internationalization supported).

### Input data file

The input data file is a text file with structure as follows.

The first row contains the number of ship types, equivalent to the number of distinct ship lengths. The following _n_ lines contain two single-whitespace-separated numbers representing ship length/type and corresponding number of ships respectively.

The following row contains the board size. The program currently supports square boards only. The following 2 lines contain _m_ single-whitespace-separated numbers that represent the total number of ship pieces in each of the _m_ board rows and columns respectively.

The final _m_ rows contain strings of _m_ characters where each character represents the field type (as defined in the [params](params.py) module) in the corresponding row and column.

### How to run the program?

Battleships requires Python 3.7 or higher. After configuring the [params](params.py) module, just run the battleships package (e.g. `python3 -m battleships`).

### How to test the program?

The unittest test code (unit and integration tests) and test fixtures are located in the [test](test) folder. To execute all tests, just run `python3 -m unittest`. **Warning:** Since the [params](params.py) module is considered a part of the program, before running the tests make sure that the module content is exactly as it is in this code repository!

### Program output

Program output is written to the output file whose name and path are specified in the [params](params.py) module. The output consists of a list of solutions followed by a message containing the number of found solutions.

### Algorithm

Basically, solving the puzzle comes down to solving each branch resulting from solving two problems:

1. There is a set of board positions which are currently not - but need to be - occupied by ship fields, i.e. each of these positions needs to be covered by a ship. The goal is to find all possible sets of remaining ships (i.e. ship remaining to be marked onto the board at that particular point in solving the puzzle), of any size, that would successfully cover the entire set of positions.

1. There is a group of _x_ ships of the same size (i.e. subfleet _x_) that needs to be marked - all ships at once - onto the board. The goal is to find all possible board "slots" in which a ship of size _x_ might be marked, and then for each _x_ slot-combination try to mark the ships into those slots.

Problem 1 has higher priority than problem 2. If problem 1 is not applicable, then problem 2 is solved. If problem 2 is also not applicable, then a solution - the current layout of ships on the board - has been found.    

## Can it be optimized?

Sure, in a number of ways, for instance by:

* Developing a GUI to collect input data and display solutions.
* Implementing input data format validation.
* Implementing additional field types e.g. for fields representing a ship of length 1, a ship's bow or stern (including ship's orientation on the board) or an unspecified ship part.
* etc.

## May I use this program?

This program is licensed under the MIT license which can be found in a separate [license file](LICENSE).

## How can I contact the author?

You can reach me by e-mail at sardinhoATgmail.com.

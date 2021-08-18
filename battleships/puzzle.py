"""This module contains data structures for handling puzzle data."""

import contextlib
import itertools
import pathlib
from typing import (
    Any,
    DefaultDict,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Set,
    TextIO,
)

import params
from battleships.board import Board, InvalidShipPlacementException
from battleships.fleet import Fleet
from battleships.grid import FieldType, FieldTypeGrid, Position
from battleships.ship import Ship


class InputData(NamedTuple):
    """Contains data parsed from the input data file."""

    grid: FieldTypeGrid
    solution_ship_fields_in_rows: List[int]
    solution_ship_fields_in_cols: List[int]
    fleet: Fleet


class Puzzle:
    """Data structure that incorporates board and fleet data.

    Board and Fleet classes are designed as separate, unrelated
    entities. Puzzle class manages the links between them.

    Class attributes:
        solutions (List[str]): String representations of puzzle solution
            boards.
        ofile (TextIO): Stream for writing output data.

    Class instance attributes:
        board (battleships.board.Board): Puzzle board.
        fleet (battleships.fleet.Fleet): Puzzle fleet.

    """

    solutions = []  # type: List[str]
    ofile = None  # type: TextIO

    def __init__(self, board: Board, fleet: Fleet) -> None:
        """Initialize a new Puzzle object.

        Args:
            board (battleships.board.Board): The puzzle board.
            fleet (battleships.fleet.Fleet): The puzzle fleet.

        """
        self.board = board
        self.fleet = fleet

    def __eq__(self, other: Any) -> bool:
        """Check if some other object is equal to self.

        Args:
            other (Any): The object to compare with self.

        Returns:
            bool: True if other object equals self, False otherwise.

        """
        if isinstance(other, self.__class__):
            return other.board == self.board and other.fleet == self.fleet
        return False

    @staticmethod
    def parse_input_data_from_file(input_file_path: pathlib.Path) -> InputData:
        """Read puzzle data from the input file.

        Args:
            input_file_path (pathlib.Path): Path to file containing
                input data.

        Returns:
            battleships.puzzle.InputData: Parsed input data.

        Raises:
            FileNotFoundError: If the input file path is invalid or
                cannot be found.

        """
        try:
            file = open(input_file_path, "r", encoding="utf-8")  # pylint: disable=R1732
        except FileNotFoundError as error:
            print(params.MESSAGES.INVALID_INPUT_FILE_PATH, file=Puzzle.ofile)
            raise error
        fleet = Fleet()
        subfleets_count = int(next(file).strip())
        for _ in range(subfleets_count):
            ship_size, number_of_ships = (int(x) for x in next(file).strip().split())
            fleet.add_ships_of_size(ship_size, number_of_ships)
        board_size = int(next(file).strip())
        solution_ship_fields_in_rows = [int(x) for x in next(file).strip().split()]
        solution_ship_fields_in_cols = [int(x) for x in next(file).strip().split()]
        grid = FieldTypeGrid()
        for _ in range(board_size):
            grid.append([FieldType(ch) for ch in next(file).strip()])
        file.close()
        return InputData(
            grid,
            solution_ship_fields_in_rows,
            solution_ship_fields_in_cols,
            fleet,
        )

    @classmethod
    def load_puzzle(cls, path: Optional[pathlib.Path] = None) -> "Puzzle":
        """Read the puzzle input file and create a Puzzle object from
        its data.

        Args:
            path (Optional[pathlib.Path]): Path to the input file.
                Defaults to None, in which case the default input file
                location is used.

        Returns:
            battleships.puzzle.Puzzle: Newly created Puzzle object.

        """
        if path:
            input_data = Puzzle.parse_input_data_from_file(path)
        else:
            input_data = Puzzle.parse_input_data_from_file(params.INPUT_FILE_PATH)
        return Puzzle(
            Board.parse_board(
                input_data.grid,
                input_data.solution_ship_fields_in_rows,
                input_data.solution_ship_fields_in_cols,
            ),
            input_data.fleet,
        )

    def ship_group_exceeds_fleet(self, ship_group: Iterable[Ship]) -> bool:
        """Check whether group of ships exceeds self's fleet.

        The fleet is considered exceeded if the number of ships of
        given size exceeds the number of fleet ships of the same size.

        Args:
            ship_group (Iterable[battleships.ship.Ship]): Group of
                ships.

        Returns:
            bool: True if the ship group exceeds self's fleet, False
                otherwise.

        """
        sizes_of_ships_in_ship_group = [ship.size for ship in ship_group]
        if any(ship.size not in self.fleet.distinct_ship_sizes for ship in ship_group):
            return True
        return any(
            self.fleet.size_of_subfleet(ship_size)
            < sizes_of_ships_in_ship_group.count(ship_size)
            for ship_size in self.fleet.distinct_ship_sizes
        )

    def get_possible_puzzles(
        self, ships_occupying_position: Dict[Position, Set[Ship]]
    ) -> List["Puzzle"]:
        """Determine a list of possible Puzzle objects in which a single
        ship from a given set covers each of the given positions.

        Positions and respective ships sets are defined in the
        ships_occupying_position input dictionary.

        Args:
            ships_occupying_position (Dict[battleships.grid.Position,
                Set[battleships.ship.Ship]]): Mapping of positions and
                sets of ships whose ship fields could cover the
                corresponding position.

        Returns:
            List[battleships.puzzle.Puzzle]: A list of possible puzzles
                in which a single ship covers each of the board
                positions in ships_occupying_position.

        """
        puzzles = []  # type: List[Puzzle]

        def get_coverings(
            ships_occupying_position: Dict[Position, Set[Ship]]
        ) -> Dict[Ship, Set[Position]]:
            """For each ship in a given set of ships determine a set of
            positions, from a given set, that the ship could cover.

            Positions and respective ships sets are defined in the
            ships_occupying_position input dictionary.

            The returned data structure is basically inverse to the
            ships_occupying_position input argument. Though technically
            not required, it aids readability a bit.

            Args:
                ships_occupying_position (Dict[
                    battleships.grid.Position, Set[battleships.ship.Ship
                    ]]): Mapping of positions and sets of ships whose
                    ship fields could cover the corresponding position.

            Returns:
                Dict[battleships.ship.Ship, Set[
                    battleships.grid.Position]]: Mapping of ships and
                    sets of positions that the corresponding ship
                    covers.

            """
            coverings = DefaultDict(set)  # type: DefaultDict[Ship, Set[Position]]
            for position, ships in ships_occupying_position.items():
                for ship in ships:
                    coverings[ship].add(position)
            return coverings

        def find_puzzles(  # pylint: disable=W9015
            ship_group: Set[Ship],
            covered_positions: Set[Position],
            positions_to_cover: List[Position],
            available_coverings: Dict[Ship, Set[Position]],
            puzzle: Puzzle,
        ) -> None:
            """Build a list of possible Puzzle objects created by
            branching a given Puzzle object and covering all given
            positions with a single ship from a given ship set.

            Depth-First Search (DFS) algorithm is used.

            Args:
                ship_group (Set[battleships.ship.Ship]): Group of
                    previously selected ships from available_coverings.
                covered_positions (Set[battleships.grid.Position]): Set
                    of positions covered by ships in ship_group.
                positions_to_cover (List[battleships.grid.Position]):
                    Positions remaining to be covered by ships.
                available_coverings(Dict[
                    battleships.ship.Ship, Set[battleships.grid.Position
                    ]]): Mapping of remaining ships and sets of
                    positions that each ship covers. Does not contain
                    any of the ships in ship_group. The sets of ships do
                    not contain any of the positions in
                    covered_positions.
                puzzle (battleships.puzzle.Puzzle): Current Puzzle
                    object.

            """
            if not positions_to_cover:
                puzzles.append(puzzle)
                return
            remaining_position = positions_to_cover[0]
            ship_candidates = [
                ship
                for ship, positions in available_coverings.items()
                if remaining_position in positions
            ]
            if not ship_candidates:
                return
            for ship_candidate in ship_candidates:
                if puzzle.board.can_fit_ship(
                    ship_candidate
                ) and not puzzle.ship_group_exceeds_fleet([ship_candidate]):
                    ship_candidate_positions = available_coverings[ship_candidate]
                    new_positions_to_cover = [
                        position
                        for position in positions_to_cover
                        if position not in ship_candidate_positions
                    ]
                    new_coverings = {
                        ship: {*ship_positions}
                        for ship, ship_positions in available_coverings.items()
                        if ship != ship_candidate
                    }
                    new_puzzle = Puzzle(
                        Board.get_copy_of(puzzle.board), Fleet.get_copy_of(puzzle.fleet)
                    )
                    new_puzzle.board.mark_ship_and_surrounding_sea(ship_candidate)
                    new_puzzle.board.mark_sea_in_series_with_no_rem_ship_fields()
                    new_puzzle.fleet.remove_ship_of_size(ship_candidate.size)
                    find_puzzles(
                        ship_group.union({ship_candidate}),
                        covered_positions.union(ship_candidate_positions),
                        new_positions_to_cover,
                        new_coverings,
                        new_puzzle,
                    )

        find_puzzles(
            set(),
            set(),
            list(ships_occupying_position.keys()),
            get_coverings(ships_occupying_position),
            self,
        )
        return puzzles

    def mark_subfleet_of_biggest_remaining_ships(self) -> None:
        """Determine the size of the largest ship remaining in the
        Puzzle fleet and mark the entire subfleet of those ships onto
        the Puzzle board.

        If the board offers more available "slots" in which all subfleet
        ships can be marked, then branch the puzzle solving by marking
        the subfleet in each possible slot combination.

        If no ships are remaining in the fleet, that means a new puzzle
        solution has been found.

        """
        if self.fleet.has_ships_remaining():
            ship_size = self.fleet.longest_ship_size
            max_possible_subfleet = self.board.get_possible_ships_of_size(ship_size)
            if len(max_possible_subfleet) == self.fleet.size_of_subfleet(ship_size):
                with contextlib.suppress(InvalidShipPlacementException):
                    self.mark_ship_group(max_possible_subfleet)
            else:
                for possible_subfleet in itertools.combinations(
                    max_possible_subfleet, self.fleet.size_of_subfleet(ship_size)
                ):
                    puzzle_branch = Puzzle(
                        Board.get_copy_of(self.board), Fleet.get_copy_of(self.fleet)
                    )
                    with contextlib.suppress(InvalidShipPlacementException):
                        puzzle_branch.mark_ship_group(set(possible_subfleet))
        else:
            self.__class__.solutions.append(self.board.repr(False))

    def mark_ship_group(self, ship_group: Iterable[Ship]) -> None:
        """Try to mark a group of ships onto Puzzle board and update
        Puzzle fleet accordingly.

        The decision on how to proceed with the solving thereafter is
        delegated to the decide_how_to_proceed method.

        Args:
            ship_group (Iterable[battleships.ship.Ship]): Group of ships
                to mark.

        """
        self.board.mark_ship_group(ship_group)
        if not self.board.is_overmarked():
            for ship in ship_group:
                self.fleet.remove_ship_of_size(ship.size)
            self.decide_how_to_proceed()

    def try_to_cover_all_ship_fields_to_be(
        self, ship_fields_to_be: Set[Position]
    ) -> None:
        """Branch puzzle solving by checking the number of puzzles in
        which all positions in a given set of board positions are
        covered with a single fleet ship.

        Args:
            ship_fields_to_be (Set[battleships.grid.Position]):
                Positions that have to be covered with ship fields.

        """
        ships_occupying_positions = self.board.get_possible_ships_occupying_positions(
            ship_fields_to_be, self.fleet.distinct_ship_sizes
        )
        puzzles = self.get_possible_puzzles(ships_occupying_positions)
        if len(puzzles) == 1:
            # only one branch -> update the current puzzle
            only_possible_puzzle = puzzles.pop()
            self.board, self.fleet = (
                only_possible_puzzle.board,
                only_possible_puzzle.fleet,
            )
            self.decide_how_to_proceed()
        else:
            for puzzle in puzzles:
                puzzle.decide_how_to_proceed()

    def decide_how_to_proceed(
        self, explicit_ship_fields_to_be: Optional[Set[Position]] = None
    ) -> None:
        """Decide how to proceed with solving the puzzle.

        If there are board positions that should contain ship pieces,
        but currently do not, then these positions must first be marked
        with ship fields by marking some ships on them. If no such
        fields can be identified, proceed with marking the subfleet of
        ships whose size equals the size of the biggest ship in the
        fleet.

        Args:
            explicit_ship_fields_to_be (Set[battleships.grid.Position]):
                Set of positions that explicitly need to be marked with
                ship fields.

        """
        ship_fields_to_be = self.board.find_definite_ship_fields_positions()
        if explicit_ship_fields_to_be:
            ship_fields_to_be.update(explicit_ship_fields_to_be)
        if ship_fields_to_be:
            self.try_to_cover_all_ship_fields_to_be(ship_fields_to_be)
        else:
            self.mark_subfleet_of_biggest_remaining_ships()

    def solve(self) -> None:
        """Start solving the puzzle."""
        ship_fields = self.board.get_ship_fields_positions()
        self.board.mark_sea_in_series_with_no_rem_ship_fields()
        self.board.mark_diagonal_sea_fields_for_positions(ship_fields)
        self.board.set_ship_fields_as_unknown(ship_fields)
        self.decide_how_to_proceed(ship_fields)

    @classmethod
    def print_solutions(cls) -> None:
        """Print puzzle solutions."""
        if cls.solutions:
            for solution in sorted(cls.solutions):
                print(solution, "\n", file=Puzzle.ofile)
            print(
                params.MESSAGES.SOLUTIONS_FOUND.format(len(cls.solutions)),
                file=Puzzle.ofile,
            )
        else:
            print(params.MESSAGES.NO_SOLUTIONS_FOUND, file=Puzzle.ofile)

    @classmethod
    def run(cls, ofile: TextIO) -> None:
        """Run the module and print the puzzle solutions."""
        Puzzle.ofile = ofile
        puzzle = Puzzle.load_puzzle()
        puzzle.solve()
        puzzle.print_solutions()

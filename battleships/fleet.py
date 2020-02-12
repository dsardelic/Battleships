"""Contains data structures for managing fleet information."""

import collections
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    MyUserDict = collections.UserDict[int, int]  # pylint: disable=C0103
else:
    MyUserDict = collections.UserDict


class Fleet(MyUserDict):
    """Represents a group of ships - a fleet.
    
    Fleet ships may vary in size. A group of ships of the same size is
    referred to as a subfleet.
    
    Fleet object contains key-value pairs. Keys represent distinct sizes
    of fleet ships (also referred to as subfleet index), while values
    represent the number of ships of size "key".
    """

    @property
    def distinct_ship_sizes(self) -> List[int]:
        """List of distinct sizes of self's ships.
        
        Returns:
            List[int]: List of distinct sizes of self's ships, sorted in
                descending order.
        
        """
        return sorted(self.keys(), reverse=True)

    @property
    def longest_ship_size(self) -> int:
        """Size of the longest ship in self.
        
        Returns:
            int: Size of the longest ship in self.
        
        Raises:
            battleships.fleet.InvalidShipSizeException: If self contains
                no ships.
        
        """
        if not self:
            raise InvalidShipSizeException
        return max(self.keys())

    def has_ships_remaining(self) -> bool:
        """Check whether self is empty, i.e. has no ships.
        
        Returns:
            bool: True is self is empty, False otherwise.
        
        """
        return len(self) > 0

    def size_of_subfleet(self, ship_size: int) -> int:
        """Size of self's subfleet ship_size (e.g. subfleet 3) i.e.
        number of self's ships of size ship_size.
        
        Args:
            ship_size (int): Size of subfleet ship_size.
        
        Returns:
            int: Number of fleet ships of size ship_size.
        
        """
        return self.get(ship_size, 0)

    def add_ships_of_size(self, ship_size: int, quantity: int) -> None:
        """Add quantity ships of size ship_size to self.
        
        Args:
            ship_size (int): Size of ships to add.
            quantity (int): Quantity of ships to add.
        
        """
        self[ship_size] = self.size_of_subfleet(ship_size) + quantity

    def remove_ship_of_size(self, ship_size: int) -> None:
        """Remove from self a single ship of size ship_size.
        
        Args:
            ship_size (int): Size of ship to remove.
        
        Raises:
            battleships.fleet.InvalidShipSizeException: If self contains
                no ships of size ship_size.
        
        """
        size_of_ship_size_subfleet = self.size_of_subfleet(ship_size)
        if not size_of_ship_size_subfleet:
            raise InvalidShipSizeException
        if size_of_ship_size_subfleet == 1:
            del self[ship_size]
        else:
            self[ship_size] -= 1

    @classmethod
    def get_copy_of(cls, original_fleet: "Fleet") -> "Fleet":
        """Create a new Fleet object as a copy of the input Fleet
        object.
        
        Args:
            original_fleet (battleships.fleet.Fleet): The fleet to copy.
        
        Returns:
            battleships.fleet.Fleet: A copy of the input Fleet object.
        
        """
        return cls(original_fleet)


class InvalidShipSizeException(Exception):
    """Raised when an illegal fleet operation was initiated."""

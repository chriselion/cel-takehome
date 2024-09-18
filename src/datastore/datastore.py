"""
Interface for a Datastore
Currently, there is only an in-memory one, but it would be simple enough to amke a database-backed implementation.
"""

import datetime
from typing import Protocol, Iterable
from src.types import ForecastPoint, Location, GridPoint


class Datastore(Protocol):
    def add_location(self, loc: Location, grid_point: GridPoint) -> None:
        """
        Add a Location and its corresponding GridPoint (determined from the NWS API)
        """
        ...

    def get_grid_point_for_location(self, loc: Location) -> GridPoint | None:
        """
        Get the GridPoint that corresponds to the given Location (or None if not found)
        """
        ...

    def get_all_locations(self) -> list[Location]:
        """
        Get the list of Locations registered.
        """
        ...

    def add_forecasts(self, loc: Location, forecasts: Iterable[ForecastPoint]):
        """
        Add a list of ForecastPoints associated with a Location.
        """
        ...

    def get_forecasts_for_datetime(
        self,
        loc: Location,
        dt: datetime.datetime,
    ) -> list[ForecastPoint]:
        """
        Get a list of Forecast points for the location at the specified time.
        """
        ...

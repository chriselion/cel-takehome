import datetime
from threading import Lock

from collections import defaultdict
from typing import Iterable, DefaultDict
from src.types import ForecastPoint, Location, GridPoint


class InMemoryDatastore:
    def __init__(self) -> None:
        # Since we'll possibly be accessing this from multiple threads (web serving and background updating),
        # We need a mutex around any access to the dictionaries.
        self._lock = Lock()

        # Mapping between Location and Grid Points
        # Locations are frozen (immutable) so they're hashable and can be used as dict keys.
        self._location_to_grid_point: dict[Location, GridPoint] = {}

        # Storage for the forecasts
        # For each (Location, forecast datetime) pair, we'll track the generated_at times and corresponding Forecast
        # This lets us quickly look up all the different forecasts at a Location for the requested time.
        self._forecasts: DefaultDict[
            tuple[Location, datetime.datetime], dict[datetime.datetime, ForecastPoint]
        ] = defaultdict(dict)

    def add_location(self, loc: Location, grid_point: GridPoint) -> None:
        with self._lock:
            self._location_to_grid_point[loc] = grid_point

    def get_grid_point_for_location(self, loc: Location) -> GridPoint | None:
        with self._lock:
            return self._location_to_grid_point.get(loc)

    def get_all_locations(self) -> list[Location]:
        with self._lock:
            return list(self._location_to_grid_point.keys())

    def add_forecasts(self, loc: Location, forecasts: Iterable[ForecastPoint]):
        with self._lock:
            for fp in forecasts:
                self._forecasts[(loc, fp.start_time)][fp.generated_at] = fp

    def get_forecasts_for_datetime(
        self, loc: Location, dt: datetime.datetime
    ) -> list[ForecastPoint]:
        with self._lock:
            forecasts_by_generated_time = self._forecasts[(loc, dt)]
            return list(forecasts_by_generated_time.values())

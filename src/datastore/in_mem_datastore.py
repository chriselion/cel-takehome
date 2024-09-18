import datetime
from collections import defaultdict
from typing import Iterable, DefaultDict
from src.types import ForecastPoint, Location, GridPoint


class InMemoryDatastore:
    def __init__(self) -> None:
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
        self._location_to_grid_point[loc] = grid_point

    def get_grid_point_for_location(self, loc: Location) -> GridPoint | None:
        return self._location_to_grid_point.get(loc)

    def get_all_locations(self) -> list[Location]:
        return list(self._location_to_grid_point.keys())

    def add_forecasts(self, loc: Location, forecasts: Iterable[ForecastPoint]):
        for fp in forecasts:
            self._forecasts[(loc, fp.start_time)][fp.generated_at] = fp

    def get_forecasts_for_datetime(
        self, loc: Location, dt: datetime.datetime
    ) -> list[ForecastPoint]:
        forecasts_by_generated_time = self._forecasts[(loc, dt)]
        return list(forecasts_by_generated_time.values())

import datetime
from typing import Iterable
from src.types import ForecastPoint, Location, GridPoint


class InMemoryDatastore:
    def __init__(self):
        pass

    def add_location(self, loc: Location, grid_point: GridPoint) -> None:
        raise NotImplementedError()

    def get_grid_point_for_location(self, loc: Location) -> GridPoint | None:
        raise NotImplementedError()

    def get_all_locations(self) -> list[Location]:
        raise NotImplementedError()

    def add_forecasts(self, loc: Location, forecasts: Iterable[ForecastPoint]):
        raise NotImplementedError()

    def get_forecasts(
        self, loc: Location, dt: datetime.datetime
    ) -> list[ForecastPoint]:
        raise NotImplementedError()

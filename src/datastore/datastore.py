import datetime
from typing import Protocol, Iterable
from src.types import ForecastPoint, Location, GridPoint


class Datastore(Protocol):
    def add_location(self, loc: Location, grid_point: GridPoint) -> None: ...
    def get_grid_point_for_location(self, loc: Location) -> GridPoint | None: ...
    def get_all_locations(self) -> list[Location]: ...

    def add_forecasts(self, loc: Location, forecasts: Iterable[ForecastPoint]): ...

    def get_forecasts(
        self,
        loc: Location,
        dt: datetime.datetime,
    ) -> list[ForecastPoint]: ...

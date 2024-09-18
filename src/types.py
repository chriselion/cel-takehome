import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    """
    A representation of a geographic location.
    The latitude and longitude are assumed to be strings of floats with 4 digits of precision
    """

    lat: str
    lon: str


@dataclass(frozen=True)
class GridPoint:
    """The NWS API grid representation of a location"""

    office: str
    grid_x: int
    grid_y: int


@dataclass(frozen=True)
class ForecastPoint:
    """
    A single temperature forecast. Stores the interval that it's for, as well as when it was generated.
    """

    temperature: int
    temperature_unit: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    generated_at: datetime.datetime

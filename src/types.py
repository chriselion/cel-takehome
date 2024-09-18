import datetime
from dataclasses import dataclass


@dataclass
class Location:
    lat: str
    lon: str


@dataclass
class GridPoint:
    office: str
    grid_x: int
    grid_y: int


@dataclass
class ForecastPoint:
    temperature: int
    temperature_unit: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    generated_at: datetime.datetime

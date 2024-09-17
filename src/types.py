from dataclasses import dataclass

@dataclass
class Location:
    lat: str
    lng: str

@dataclass
class GridPoint:
    office: str
    grid_x: int
    grid_y: int
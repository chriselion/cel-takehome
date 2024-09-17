from src.types import Location
from src import weather_gov_api

def test_location_to_grid():
    loc = Location("39.7456", "-97.0892")
    grid_point = weather_gov_api.get_grid_point_for_location(loc)
    assert grid_point.grid_x == 32
    assert grid_point.grid_y == 81
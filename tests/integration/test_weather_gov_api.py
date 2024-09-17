import datetime

from src.types import Location
from src import weather_gov_api


def test_location_to_grid():
    loc = Location("39.7456", "-97.0892")
    grid_point = weather_gov_api.get_grid_point_for_location(loc)
    assert grid_point.grid_x == 32
    assert grid_point.grid_y == 81
    assert grid_point.office == "TOP"


def test_get_forecast_for_grid_point():
    loc = Location("39.7456", "-97.0892")
    grid_point = weather_gov_api.get_grid_point_for_location(loc)
    forecast = weather_gov_api.get_forecast_for_grid_point(grid_point)
    assert forecast
    now = datetime.datetime.now(datetime.UTC)
    for f in forecast:
        assert f.temperature >= -459.67  # absolute zero
        assert f.temperature <= 212  # boiling point of water
        assert f.generated_at <= now
        assert f.start_time < f.end_time


def test_get_forecast_for_grid_point_max_start():
    """
    Make sure that passing a max_start_time results in a shorter forecast.
    TODO Move this to a unit test instead.
    """
    now = datetime.datetime.now(datetime.UTC)
    max_start = now + datetime.timedelta(hours=5)

    loc = Location("39.7456", "-97.0892")
    grid_point = weather_gov_api.get_grid_point_for_location(loc)
    full_forecast = weather_gov_api.get_forecast_for_grid_point(grid_point)
    truncated_forecast = weather_gov_api.get_forecast_for_grid_point(
        grid_point, max_start_time=max_start
    )
    assert len(full_forecast) > len(truncated_forecast)
    assert full_forecast[0] == truncated_forecast[0]

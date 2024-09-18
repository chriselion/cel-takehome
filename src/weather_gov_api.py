"""
Simple API for querying the National Weather Service API
See https://www.weather.gov/documentation/services-web-api
"""

import datetime
import requests
from src.types import Location, GridPoint, ForecastPoint


def get_grid_point_for_location(loc: Location) -> GridPoint:
    resp = requests.get(f"https://api.weather.gov/points/{loc.lat},{loc.lon}")
    resp.raise_for_status()

    resp_json = resp.json()
    props = resp_json["properties"]

    return GridPoint(
        office=props["gridId"],
        grid_x=props["gridX"],
        grid_y=props["gridY"],
    )


def get_forecast_for_grid_point(
    grid: GridPoint,
    max_start_time: datetime.datetime | None = None,
) -> list[ForecastPoint]:
    """
    Get a list of forecasts for the grid point.
    :param grid: The grid point to query
    :param max_start_time: The maximum start time for forecasts.
        Forecast intervals that start after this will be ignored.
    :return: A list of ForecastPoints
    """
    url = f"https://api.weather.gov/gridpoints/{grid.office}/{grid.grid_x},{grid.grid_y}/forecast/hourly"
    resp = requests.get(url)
    resp.raise_for_status()

    resp_json = resp.json()
    generated_at_str = resp_json["properties"]["generatedAt"]
    generated_at = datetime.datetime.fromisoformat(generated_at_str)
    out = []
    for p in resp_json["properties"]["periods"]:
        fp = ForecastPoint(
            temperature=p["temperature"],
            temperature_unit=p["temperatureUnit"],
            start_time=datetime.datetime.fromisoformat(p["startTime"]),
            end_time=datetime.datetime.fromisoformat(p["endTime"]),
            generated_at=generated_at,
        )
        if max_start_time and fp.start_time > max_start_time:
            # Out of range, just ignore it
            continue
        out.append(fp)
    return out

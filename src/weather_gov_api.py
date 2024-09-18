"""
Simple API for querying the National Weather Service API
See https://www.weather.gov/documentation/services-web-api
"""

import datetime
import requests
from src.types import Location, GridPoint, ForecastPoint

# Always pass a timeout to requests, otherwise it can hang forever!
DEFAULT_TIMEOUT_SECONDS = 30


def get_grid_point_for_location(
    loc: Location, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
) -> GridPoint:
    """
    Looks up the GridPoint for a location from the NWS API.
    """
    resp = requests.get(
        f"https://api.weather.gov/points/{loc.lat},{loc.lon}", timeout=timeout_seconds
    )
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
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> list[ForecastPoint]:
    """
    Get a list of forecasts for the grid point.
    :param grid: The grid point to query
    :param max_start_time: The maximum start time for forecasts.
        Forecast intervals that start after this will be ignored.
    :param timeout_seconds: Timeout passed to requests
    :return: A list of ForecastPoints
    """
    url = f"https://api.weather.gov/gridpoints/{grid.office}/{grid.grid_x},{grid.grid_y}/forecast/hourly"
    resp = requests.get(url, timeout=timeout_seconds)
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

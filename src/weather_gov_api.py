import requests
from src.types import Location, GridPoint


def get_grid_point_for_location(loc: Location) -> GridPoint:
    resp = requests.get(f"https://api.weather.gov/points/{loc.lat},{loc.lng}")
    resp.raise_for_status()

    resp_json = resp.json()
    props = resp_json["properties"]

    return GridPoint(
        office=props["gridId"],
        grid_x=props["gridX"],
        grid_y=props["gridY"],
    )

import datetime
import logging

from src.datastore.datastore import Datastore
from src.types import Location
from src import weather_gov_api


def update_forecasts_for_location(
    loc: Location, ds: Datastore, max_hours_ahead: int = 72
) -> None:
    max_start_time = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(
        hours=max_hours_ahead
    )
    grid_point = ds.get_grid_point_for_location(loc)
    if not grid_point:
        # This shouldn't ever happen since the location is already in the datastore
        # But needed to keep type-checking happy.
        logging.warning(f"Didn't found datastore gridpoint for location {loc}")
        return
    forecasts = weather_gov_api.get_forecast_for_grid_point(grid_point, max_start_time)
    ds.add_forecasts(loc, forecasts)


def update_all_forecasts(ds: Datastore, max_hours_ahead: int = 72):
    all_locs = ds.get_all_locations()
    # TODO if we have multiple locations that map to the same gridpoint, this will fetch redundant forecasts
    # We could dedupe based on grid points.
    for loc in all_locs:
        update_forecasts_for_location(loc, ds, max_hours_ahead)

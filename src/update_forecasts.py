import time
import datetime
import logging
import threading

from src.datastore.datastore import Datastore
from src.types import Location
from src import weather_gov_api


def update_forecasts_for_location(
    loc: Location, ds: Datastore, max_hours_ahead
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


def update_all_forecasts(ds: Datastore, max_hours_ahead: int):
    try:
        all_locs = ds.get_all_locations()
    except Exception:
        # This can't happen with the in-memory datastore, but could be a problem if we used a database.
        logging.exception(
            "Unable to get list of locations. Check logs for more details"
        )
        # Can't do anything, so just exit
        return

    # TODO if we have multiple locations that map to the same gridpoint, this will fetch redundant forecasts
    # We could dedupe based on grid points.
    for loc in all_locs:
        try:
            update_forecasts_for_location(loc, ds, max_hours_ahead)
        except Exception:
            # Make sure that a failure in one location doesn't block updates in another.
            logging.exception(f"Error updating forecasts for location {loc}")


def update_forecasts_loop(
    ds: Datastore, *, max_hours_ahead: int, refresh_interval_seconds: int
):
    logging.info(
        f"Starting update loop. Will refresh every {refresh_interval_seconds} seconds"
    )
    while True:
        start_time = time.time()
        logging.info("Updating all forecasts")
        update_all_forecasts(ds, max_hours_ahead=max_hours_ahead)
        elapsed = time.time() - start_time

        if elapsed < refresh_interval_seconds:
            # Sleep until the next interval
            sleep_time = refresh_interval_seconds - elapsed
            logging.info(f"Done updating; sleeping for {round(sleep_time, 4)} seconds")
            time.sleep(sleep_time)
        else:
            logging.warning("Updating took longer than refresh interval. Not sleeping")


def spawn_background_update(
    ds: Datastore, *, max_hours_ahead: int, refresh_interval_seconds: int
):
    update_thread = threading.Thread(
        target=update_forecasts_loop,
        args=(ds,),
        kwargs=dict(
            max_hours_ahead=max_hours_ahead,
            refresh_interval_seconds=refresh_interval_seconds,
        ),
        # Make sure this doesn't block shutting the app down
        daemon=True,
    )
    update_thread.start()

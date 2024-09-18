import datetime
import logging
from logging.config import dictConfig


from flask import Flask, request, abort

import settings
from src.datastore.datastore import Datastore
from src.datastore.in_mem_datastore import InMemoryDatastore
from src import weather_gov_api
from src.types import Location
from src import update_forecasts

app = Flask(__name__)

# The "global" datastore used by the application.
_datastore = InMemoryDatastore()


def get_data_store() -> Datastore:
    """
    Wrapper around access to the "global" datastore, so that we can mock this in unit tests.
    """
    return _datastore


# Default flask logging setup, from https://flask.palletsprojects.com/en/2.3.x/logging/#basic-configuration
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


@app.route("/location", methods=["POST"])
def add_location() -> str:
    # TODO replace with something like pydantic to make parsing and validating easier.
    req_body = request.json
    loc_dict = req_body["location"]
    # TODO validate lat and lon are string representations of floats
    loc = Location(loc_dict["lat"], loc_dict["lon"])

    # See if we have this Location's grid point already
    datastore = get_data_store()

    grid_point = datastore.get_grid_point_for_location(loc)
    if grid_point:
        logging.info("Found existing grid point for location")
    else:
        # If not, look it up from the API
        logging.info("Didn't find grid point in datastore, looking up from API")
        grid_point = weather_gov_api.get_grid_point_for_location(loc)
        # TODO handle errors from the API here and return nicer error messages

        # Save the Location->GridPoint mapping for future use
        datastore.add_location(loc, grid_point)

        # Fetch forecasts, so that we have them available right away
        logging.info("Fetching forecasts for new location")
        update_forecasts.update_forecasts_for_location(
            loc, datastore, settings.MAX_LOOK_AHEAD_HOURS
        )

    return "ok"


@app.route("/forecasts", methods=["POST", "GET"])
def get_forecasts() -> int | dict:
    # TODO decide on a recommended method for this.
    # My understanding is that GETs with JSON bodies aren't recommended
    # (see https://stackoverflow.com/questions/978061/http-get-with-request-body)
    # But GET seems more appropriate since there are no side-effects here.
    # As a compromise that will leave nobody happy, both methods are accepted.

    req_body = request.json
    # Extract the fields from the request
    loc_dict = req_body["location"]
    loc = Location(loc_dict["lat"], loc_dict["lon"])

    date_str = req_body.get("date")
    date = datetime.date.fromisoformat(date_str)
    hour = int(req_body.get("hour"))
    dt = datetime.datetime(
        year=date.year, month=date.month, day=date.day, hour=hour, tzinfo=datetime.UTC
    )

    # Get the forecasts we've recorded, and return them
    datastore = get_data_store()
    forecasts = datastore.get_forecasts_for_datetime(loc, dt)

    if not forecasts:
        # TODO better error response
        logging.info("No forecasts found")
        abort(404)

    logging.info(f"Found {len(forecasts)} forecasts for {dt}")
    # TODO make sure all forecasts have the same units
    max_temp = max(f.temperature for f in forecasts)
    min_temp = min(f.temperature for f in forecasts)
    units = forecasts[0].temperature_unit
    return {
        "max_forecast_temperature": max_temp,
        "min_forecast_temperature": min_temp,
        "temperature_units": units,
    }


# start a background thread that will periodically update all registered locations
update_forecasts.spawn_background_update(
    get_data_store(),
    max_hours_ahead=settings.MAX_LOOK_AHEAD_HOURS,
    refresh_interval_seconds=settings.FORECAST_REFRESH_INTERNAL_SECONDS,
)

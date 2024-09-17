import datetime
import logging

from flask import Flask, request, abort

from src.datastore.datastore import Datastore
from src.datastore.in_mem_datastore import InMemoryDatastore
from src import weather_gov_api
from src.types import Location  # noqa

logger = logging.getLogger(__name__)
logging.basicConfig()

app = Flask(__name__)
_datastore = InMemoryDatastore()


def get_data_store() -> Datastore:
    return _datastore


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/location", methods=["POST"])
def add_location() -> str:
    # TODO replace with something like pydantic to make parsing and validating easier.
    req_body = request.json
    loc_dict = req_body["location"]
    lat = loc_dict["lat"]
    lon = loc_dict["lon"]
    # TODO validate lat and lon are string representations of floats
    loc = Location(lat, lon)

    # See if we have this Location's grid point already
    datastore = get_data_store()

    grid_point = datastore.get_grid_point_for_location(loc)
    # breakpoint()
    if grid_point:
        logger.info("Found existing grid point for location")
    else:
        # If not, look it up from the API
        logger.info("Didn't find grid point in datastore, looking up from API")
        grid_point = weather_gov_api.get_grid_point_for_location(loc)
        # TODO handle errors from the API here and return nicer error messages

        # Save the Location->GridPoint mapping for future use
        datastore.add_location(loc, grid_point)
        return "ok"

    return "ok"


@app.route("/forecasts", methods=["POST"])
def get_forecasts() -> int | dict:
    req_body = request.json
    loc = Location(req_body["lat"], req_body["lon"])
    date_str = req_body.get("date")
    date = datetime.date.fromisoformat(date_str)
    hour = int(req_body.get("hour"))
    dt = datetime.datetime(
        year=date.year, month=date.month, day=date.day, hour=hour, tzinfo=datetime.UTC
    )

    # Get the forecasts we've recorded, and return them
    datastore = get_data_store()
    forecasts = datastore.get_forecasts(loc, dt)

    if not forecasts:
        abort(404)

    # TODO make sure all forecasts have the same units
    max_temp = max(f.temperature for f in forecasts)
    min_temp = min(f.temperature for f in forecasts)
    units = forecasts[0].temperature_unit
    return {
        "max_forecast_temperature": max_temp,
        "min_forecast_temperature": min_temp,
        "temperature_units": units,
    }

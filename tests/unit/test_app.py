import datetime

import app
from unittest import mock

from src.types import GridPoint, Location, ForecastPoint
import src.weather_gov_api
import src.update_forecasts

LAT = "39.7456"
LON = "-97.0892"
TEST_JSON_LOCATION_BODY = {"location": {"lat": LAT, "lon": LON}}

TEST_JSON_FORECASTS_BODY = {
    "location": {"lat": LAT, "lon": LON},
    "date": "2024-09-18",
    "hour": 16,
}

TEST_LOCATION = Location(LAT, LON)
TEST_GRID_POINT = GridPoint("test", 42, 42)


@mock.patch.object(app, "get_data_store")
def test_add_location_existing_location(mock_get_datastore):
    client = app.app.test_client()
    mock_datastore = mock_get_datastore()
    # Test the case where we already know the grid point for the lat/lon
    mock_datastore.get_grid_point_for_location.return_value = TEST_GRID_POINT

    resp = client.post("/location", json=TEST_JSON_LOCATION_BODY)

    # Since the mock returned a GridPoint, the app didn't try to add a point to the database.
    mock_datastore.add_location.assert_not_called()
    assert resp.status_code == 200, resp.data


@mock.patch.object(src.update_forecasts, "update_forecasts_for_location")
@mock.patch.object(src.weather_gov_api, "get_grid_point_for_location")
@mock.patch.object(app, "get_data_store")
def test_add_location_unknown_location(
    mock_get_datastore, mock_api_get_grid, mock_update_forecasts
):
    client = app.app.test_client()
    mock_datastore = mock_get_datastore()
    # Test the case where we don't know the grid point, so have to look it up from the API
    mock_datastore.get_grid_point_for_location.return_value = None
    mock_api_get_grid.return_value = TEST_GRID_POINT

    resp = client.post("/location", json=TEST_JSON_LOCATION_BODY)

    # Make sure that we called the remote API with the location, and that we added it to the database
    mock_api_get_grid.assert_called_once_with(TEST_LOCATION)
    mock_datastore.add_location.assert_called_once_with(TEST_LOCATION, TEST_GRID_POINT)
    # Make sure we also updated the forecasts since it's the first time we've seen this point.
    mock_update_forecasts.assert_called_with(TEST_LOCATION, mock_datastore, mock.ANY)
    assert resp.status_code == 200, resp.data


@mock.patch.object(app, "get_data_store")
def test_get_forecasts_empty_list(mock_get_datastore):
    client = app.app.test_client()
    mock_datastore = mock_get_datastore()
    mock_datastore.get_forecasts_for_datetime.return_value = []

    resp = client.post("/forecasts", json=TEST_JSON_FORECASTS_BODY)
    assert resp.status_code == 404, resp.data


@mock.patch.object(app, "get_data_store")
def test_get_forecasts(mock_get_datastore):
    client = app.app.test_client()
    mock_datastore = mock_get_datastore()
    high_temp = 42
    low_temp = 37
    # The actual datetimes don't matter in the mock
    now = datetime.datetime.now()
    mock_datastore.get_forecasts_for_datetime.return_value = [
        ForecastPoint(
            high_temp,
            "F",
            now,
            now + datetime.timedelta(hours=1),
            now - datetime.timedelta(hours=1),
        ),
        ForecastPoint(
            low_temp,
            "F",
            now,
            now + datetime.timedelta(hours=1),
            now - datetime.timedelta(hours=2),
        ),
        # Extra temp in the middle
        ForecastPoint(
            (low_temp + high_temp) // 2,
            "F",
            now,
            now + datetime.timedelta(hours=1),
            now - datetime.timedelta(hours=3),
        ),
    ]

    resp = client.post("/forecasts", json=TEST_JSON_FORECASTS_BODY)
    assert resp.status_code == 200, resp.data

    resp_json = resp.json
    assert resp_json["max_forecast_temperature"] == high_temp
    assert resp_json["min_forecast_temperature"] == low_temp
    assert resp_json["temperature_units"] == "F"

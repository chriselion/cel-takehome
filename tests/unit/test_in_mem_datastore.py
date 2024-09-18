import datetime

from src.datastore.in_mem_datastore import InMemoryDatastore
from src.types import Location, GridPoint, ForecastPoint

LOC_CHI = Location("39.7456", "-97.0892")
GRID_CHI = GridPoint("CHI", 19, 85)

LOC_SFO = Location("37.6191", "-122.3816")
GRID_SFO = GridPoint("SFO", 18, 49)

LOC_LAX = Location("33.9422", "-118.4036")


def test_loc_grid_points():
    ds = InMemoryDatastore()

    ds.add_location(LOC_CHI, GRID_CHI)
    ds.add_location(LOC_SFO, GRID_SFO)

    assert ds.get_grid_point_for_location(LOC_CHI) == GRID_CHI
    assert ds.get_grid_point_for_location(LOC_SFO) == GRID_SFO
    assert ds.get_grid_point_for_location(LOC_LAX) is None

    assert set(ds.get_all_locations()) == {LOC_CHI, LOC_SFO}


def test_forecasts():
    now = datetime.datetime.now()
    all_chi_forecasts = [
        ForecastPoint(
            10,  # It's chilly in Chicago
            "F",
            start_time=now,
            end_time=now + datetime.timedelta(hours=1),
            generated_at=now
            - datetime.timedelta(hours=1),  # Prediction made one hour ago
        ),
        ForecastPoint(
            12,
            "F",
            start_time=now,
            end_time=now + datetime.timedelta(hours=1),
            generated_at=now
            - datetime.timedelta(hours=2),  # Prediction made two hours ago
        ),
        # Prediction for the future, we don't expect to see this one when getting forecasts for "now"
        ForecastPoint(
            -2,
            "F",
            start_time=now + datetime.timedelta(hours=2),
            end_time=now + datetime.timedelta(hours=3),
            generated_at=now
            - datetime.timedelta(hours=2),  # Prediction made two hours ago
        ),
    ]
    all_sfo_forecasts = [
        ForecastPoint(
            60,  # A little better in SF, probably foggy too
            "F",
            start_time=now,
            end_time=now + datetime.timedelta(hours=1),
            generated_at=now
            - datetime.timedelta(hours=1),  # Prediction made one hour ago
        ),
        ForecastPoint(
            62,  # A little better in SF, probably foggy too
            "F",
            start_time=now,
            end_time=now + datetime.timedelta(hours=1),
            generated_at=now
            - datetime.timedelta(hours=2),  # Prediction made two hours ago
        ),
    ]

    ds = InMemoryDatastore()
    ds.add_forecasts(LOC_CHI, all_chi_forecasts)
    ds.add_forecasts(LOC_SFO, all_sfo_forecasts)

    chi_forecasts_now = ds.get_forecasts_for_datetime(LOC_CHI, now)
    assert len(chi_forecasts_now) == 2
    # Make sure we got the two expected temps
    assert {fp.temperature for fp in chi_forecasts_now} == {10, 12}

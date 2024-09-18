"""
This is an end-to-end "test" that demonstrates the API
It is meant to be run from the host OS, while the container is running.
"""

import datetime
import requests

URL = "http://localhost:8080"


def main():
    # Register SFO as a tracking location
    lat, lon = "37.6191", "-122.3816"
    print("Registering location")
    create_resp = requests.post(
        URL + "/location",
        json={"location": {"lat": lat, "lon": lon}},
    )
    create_resp.raise_for_status()

    # Get the forecast for the next hour
    now = datetime.datetime.now(tz=datetime.UTC)
    day = datetime.date.today().isoformat()
    hour = now.hour + 1
    print(f"Requesting forecasts for {day=} {hour=}")
    forecast_resp = requests.post(
        URL + "/forecasts",
        json={"location": {"lat": lat, "lon": lon}, "date": day, "hour": hour},
    )
    forecast_resp.raise_for_status()
    print(forecast_resp.json())


if __name__ == "__main__":
    main()

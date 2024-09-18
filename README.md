# cel-takehome
Community Energy Labs takehome assignment

## Usage:
```commandline
# Build the image
docker build . -t cel-takehome:local

# Run the server in a container
docker run --rm -it -p 8080:8080 -v $(pwd):/app cel-takehome:local

# Run unit and integration tests
docker run --rm -it -v $(pwd):/app cel-takehome:local pytest

# Get a shell for local development
docker run --rm -it -v $(pwd):/app cel-takehome:local bash
```
When the container is running, in another terminal, you can run `python end_to_end.py` to make some example requests
against it.

This was only tested on MacOS; the Docker networking might be slightly different on other OS's.

## API
`POST /location` accepts a JSON body with the format
```json
{
    "location": {
        "lat": "39.7456",
        "lon": "-97.0892"
    }
}
```

`POST /forecasts` and `GET /forecasts` accept a JSON body with the format
```json
{
    "location": {
        "lat": "39.7456",
        "lon": "-97.0892"
    },
    "date": "2024-09-18",
    "hour": 20
}
```
and returns
```json
{
  "max_forecast_temperature": 65,
  "min_forecast_temperature": 65,
  "temperature_units": "F"
}
```


## Assumptions Made:
* Assumes that the lat-lon -> grid point mapping from the National Weather Service API doesn't change. It would be
simple enough to refetch the grid point, say, once/day the first time the location is used.
* Assumes that all forecasts with the same "generatedAt" timestamp for a grid point are the same. The "generatedAt"
time is used to dedupe forecasts, so if the forecast does change, the old value will likely be overwritten.
* Uses the start time of the returned forecast "period" from the Weather API. Assumes the periods are also one hour in
duration.
* Assumes that all forecast temperatures are in the same units. Ideally we'd normalize them to Celcius when querying.

One potential deviation from the spec is that forecasts for a location the first time it is registered with the
`/location` endpoint, so that it is immediately available for requests. A narrow reading of the description is that
this wouldn't happen until the next background update interval, but that's bad user experience.

## Configuration:
The following environment variables can be used to configure the application.
* `MAX_LOOK_AHEAD_HOURS` - the number of hours ahead to fetch forecast. Defaults to 72 hours
* `FORECAST_REFRESH_INTERNAL_SECONDS` - the interval the updated forecasts are fetched from the NWS API.
Defaults to 3600 seconds (1 hour).

## Future Work
This is obviously not production quality. Given more time, I'd implement more of the following:
* Error handling - any errors from the NWS API will likely result in a 500 from the service. I should try to
anticipate what could go wrong, and return better erorrs (or at least specific error messages).
* Input validation - currently fields are read directly from the request body dictionary and not sanitized. A better
approach would be to use something like pydantic to define the request and response formats as python obects, and
convert those to/from JSON with better validation (e.g. that lat and lon are strings of floats).
* Database - the current implementation store everything in memory; it should use a database like postgres intsead.
* WSGI - this just uses "vanilla" Flask as the webserver; it should run e.g. gunicorn or uwsgi
* Better testing on the update thread - the update loop should be robust currently (i.e. it will keep running if
there's an error accessing the NWS API), but I didn't have time to let it run and see if it kept updating.
* Observability - should add e.g. prometheus or OpenTelemetry to track service requests, errors, etc.
* Efficiency - there are some potential improvements to reduce API calls for locations that are nearby (i.e. they have
the same grid point in the NWS's API).
* Some other miscellaneous potential improvements are noted inline with "TODO".

## Resources used
* Flask documentation: https://flask.palletsprojects.com/en/3.0.x/quickstart and https://flask.palletsprojects.com/en/1.1.x/testing/
* Python threading documentation: https://docs.python.org/3/library/threading.html#with-locks
* Docker networking: https://docs.docker.com/engine/network/

**No AI (ChatGPT, etc) was used to write this.**

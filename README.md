# cel-takehome
Community Energy Labs takehome assignment

## Usage:
```commandline
docker build . -t cel-takehome:local

# Run the server
docker run --rm -it -p 8080:8080 -v $(pwd):/app cel-takehome:local

# Local development
docker run --rm -it -v $(pwd):/app cel-takehome:local bash
```

## Assumptions Made:
* Assumes that the lat-lon -> grid point mapping from the National Weather Service API doesn't change. It would be
simple enough to refetch the grid point, say, once/day the first time the location is used.
* Assumes that all forecasts with the same "generatedAt" timestamp for a grid point are the same. The "generatedAt"
time is used to dedupe forecasts, so if the forecast does change, the old value will likely be overwritten.
* Uses the start time of the returned forecast "period" from the Weather API. Assumes the periods are also one hour in
duration.

## Configuration:
The following environment variables can be used to configure the application.
* `MAX_LOOK_AHEAD_HOURS` - the number of hours ahead to fetch forecast. Defaults to 72 hours
* `FORECAST_REFRESH_INTERNAL_SECONDS` - the interval the updated forecasts are fetched from the NWS API.
Defaults to 3600 seconds (1 hour).

# cel-takehome
Community Energy Labs takehome assignment

Usage:
```commandline
docker build . -t cel-takehome:local

# Run the server
docker run --rm -it -p 8080:8080 -v $(pwd):/app cel-takehome:local

# Local development
docker run --rm -it -v $(pwd):/app cel-takehome:local bash
```

Assumptions Made:
* Assumes that the lat-lon -> grid point mapping from the National Weather Service API doesn't change. It would be
simple enough to refetch the grid point, say, once/day the first time the location is used.
* Assumes that all forecasts with the same "generatedAt" timestamp for a grid point are the same. The "generatedAt"
time is used to dedupe forecasts, so if the forecast does change, the old value will likely be overwritten.
* Uses the start time of the returned forecast "period" from the Weather API. Assumes the periods are also one hour in
duration.

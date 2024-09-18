import os

# See readme for descriptions
MAX_LOOK_AHEAD_HOURS = int(os.getenv("MAX_LOOK_AHEAD_HOURS", "72"))
FORECAST_REFRESH_INTERNAL_SECONDS = int(
    os.getenv("FORECAST_REFRESH_INTERNAL_SECONDS", "3600")
)

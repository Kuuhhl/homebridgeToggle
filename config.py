import os

# URL to synced files that contains 1 or 0 in every line, split by comma
if os.environ.get("LOCATION_SYNC_FILE_URLS"):
    sync_file_urls = [
        x.strip() for x in os.environ.get("LOCATION_SYNC_FILE_URLS").split(",")
    ]
elif os.environ.get("LOCATION_SYNC_FILE_URL"):
    sync_file_urls = [os.environ.get("LOCATION_SYNC_FILE_URL")]

# URL to homebridge instance
base_url = os.environ.get("HOMEBRIDGE_BASE_URL")

# Unique IDs of lights to toggle
lights_uniqueIds = []

# amount of time to wait before starting in seconds (e.g. to wait for homebridge to start)
INITIAL_SLEEP = 30

# polling interval in seconds
POLLING_INTERVAL = 30

# Homebridge username
homebridge_username = os.environ.get("HOMEBRIDGE_USERNAME")

# Homebridge password
homebridge_password = os.environ.get("HOMEBRIDGE_PASSWORD")

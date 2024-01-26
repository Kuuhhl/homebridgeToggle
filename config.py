import os

# URL to synced file that contains 1 or 0 in every line
sync_file_url = os.environ.get("LOCATION_SYNC_FILE_URL")

# URL to homebridge instance
base_url = os.environ.get("HOMEBRIDGE_BASE_URL")

# Unique IDs of lights to toggle
lights_uniqueIds = []

# polling interval in seconds
POLLING_INTERVAL = 30

# Homebridge username
homebridge_username = os.environ.get("HOMEBRIDGE_USERNAME")

# Homebridge password
homebridge_password = os.environ.get("HOMEBRIDGE_PASSWORD")

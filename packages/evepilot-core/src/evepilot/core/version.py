"""Version and build metadata."""

import os

APP_NAME = "EvePilot"
APP_VERSION = "0.3.0"
API_VERSION = "1"

RELEASE_CHANNEL = os.getenv("EVEPILOT_RELEASE_CHANNEL", "dev")
GIT_SHA = os.getenv("EVEPILOT_GIT_SHA", "unknown")
BUILD_TIME = os.getenv("EVEPILOT_BUILD_TIME", "unknown")

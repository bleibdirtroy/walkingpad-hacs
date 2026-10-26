"""Konstanten für die WalkingPad Integration."""

from typing import Final

DOMAIN: Final = "walkingpad"

# Config
CONF_ADDRESS: Final = "address"
CONF_NAME: Final = "name"
CONF_SCAN_TIMEOUT: Final = "scan_timeout"

# Default Werte
DEFAULT_NAME: Final = "WalkingPad"
DEFAULT_SCAN_TIMEOUT: Final = 10

# Geschwindigkeiten
MIN_SPEED: Final = 0.5
MAX_SPEED: Final = 6.0
SPEED_STEP: Final = 0.5

# Update Interval
UPDATE_INTERVAL: Final = 1  # Sekunden

# Service Namen
SERVICE_START: Final = "start"
SERVICE_STOP: Final = "stop"
SERVICE_SET_SPEED: Final = "set_speed"

# Attribute
ATTR_SPEED: Final = "speed"
ATTR_STEPS: Final = "steps"
ATTR_DISTANCE: Final = "distance"
ATTR_TIME: Final = "time"
ATTR_CALORIES: Final = "calories"
ATTR_BELT_STATE: Final = "belt_state"
ATTR_MODE: Final = "mode"

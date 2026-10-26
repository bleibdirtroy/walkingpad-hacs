"""Sensoren für WalkingPad."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfLength,
    UnitOfTime,
    UnitOfSpeed,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WalkingPadCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setzt die Sensoren ein."""
    coordinator: WalkingPadCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        WalkingPadSpeedSensor(coordinator, entry),
        WalkingPadStepsSensor(coordinator, entry),
        WalkingPadDistanceSensor(coordinator, entry),
        WalkingPadTimeSensor(coordinator, entry),
        WalkingPadCaloriesSensor(coordinator, entry),
        WalkingPadStatusSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class WalkingPadSensorBase(CoordinatorEntity, SensorEntity):
    """Basisklasse für WalkingPad Sensoren."""

    def __init__(
        self,
        coordinator: WalkingPadCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialisiert den Sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get("name", "WalkingPad"),
            manufacturer="KingSmith",
            model="WalkingPad",
            sw_version="1.0",
            connections={(entry.data["address"])},
        )


class WalkingPadSpeedSensor(WalkingPadSensorBase):
    """Geschwindigkeitssensor."""

    _attr_name = "Geschwindigkeit"
    _attr_unique_id_suffix = "speed"
    _attr_device_class = SensorDeviceClass.SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_icon = "mdi:speedometer"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_speed"

    @property
    def native_value(self) -> float | None:
        """Aktuelle Geschwindigkeit."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("speed", 0), 1)
        return None


class WalkingPadStepsSensor(WalkingPadSensorBase):
    """Schrittzähler."""

    _attr_name = "Schritte"
    _attr_unique_id_suffix = "steps"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "Schritte"
    _attr_icon = "mdi:shoe-print"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_steps"

    @property
    def native_value(self) -> int | None:
        """Aktuelle Schrittzahl."""
        if self.coordinator.data:
            return self.coordinator.data.get("steps", 0)
        return None


class WalkingPadDistanceSensor(WalkingPadSensorBase):
    """Distanzsensor."""

    _attr_name = "Distanz"
    _attr_unique_id_suffix = "distance"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:map-marker-distance"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_distance"

    @property
    def native_value(self) -> float | None:
        """Aktuelle Distanz in km."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("distance", 0), 2)
        return None


class WalkingPadTimeSensor(WalkingPadSensorBase):
    """Zeitsensor."""

    _attr_name = "Aktive Zeit"
    _attr_unique_id_suffix = "time"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:timer-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_time"

    @property
    def native_value(self) -> int | None:
        """Aktive Zeit in Sekunden."""
        if self.coordinator.data:
            return self.coordinator.data.get("time", 0)
        return None


class WalkingPadCaloriesSensor(WalkingPadSensorBase):
    """Kaloriensensor."""

    _attr_name = "Kalorien"
    _attr_unique_id_suffix = "calories"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kcal"
    _attr_icon = "mdi:fire"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_calories"

    @property
    def native_value(self) -> int | None:
        """Geschätzte Kalorien."""
        if self.coordinator.data:
            return self.coordinator.data.get("calories", 0)
        return None


class WalkingPadStatusSensor(WalkingPadSensorBase):
    """Status-Sensor."""

    _attr_name = "Status"
    _attr_unique_id_suffix = "status"
    _attr_icon = "mdi:information-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self) -> str | None:
        """Aktueller Status."""
        if not self.coordinator.data:
            return "unavailable"
        belt_state = self.coordinator.data.get("belt_state", 0)
        states = {0: "Bereit", 1: "Läuft", 2: "Pause", 3: "Stop"}
        return states.get(belt_state, "Unbekannt")

    @property
    def icon(self) -> str:
        """Dynamisches Icon basierend auf Status."""
        if not self.coordinator.data:
            return "mdi:help-circle-outline"
        belt_state = self.coordinator.data.get("belt_state", 0)
        icons = {
            0: "mdi:power-standby",
            1: "mdi:run-fast",
            2: "mdi:pause-circle-outline",
            3: "mdi:stop-circle-outline",
        }
        return icons.get(belt_state, "mdi:help-circle-outline")

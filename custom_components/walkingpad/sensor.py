"""Sensoren für WalkingPad."""

import logging

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
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WalkingPadCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setzt die Sensoren ein."""
    coordinator: WalkingPadCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        # Aktuelle Session
        WalkingPadSpeedSensor(coordinator, entry),
        WalkingPadStepsSensor(coordinator, entry),
        WalkingPadDistanceSensor(coordinator, entry),
        WalkingPadTimeSensor(coordinator, entry),
        WalkingPadCaloriesSensor(coordinator, entry),
        WalkingPadStatusSensor(coordinator, entry),
        # Gesamt-Statistik (persistent über Neustarts)
        WalkingPadTotalStepsSensor(coordinator, entry),
        WalkingPadTotalDistanceSensor(coordinator, entry),
        WalkingPadTotalCaloriesSensor(coordinator, entry),
    ]

    async_add_entities(entities)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    """Erstellt die Device Info."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.data.get("name", "WalkingPad"),
        manufacturer="KingSmith",
        model="WalkingPad",
        sw_version="1.0",
    )


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
        self._attr_device_info = _device_info(entry)


# ═══════════════════════════════════════════════════════════════════════
# Aktuelle Session Sensoren (vom Gerät, werden bei Neustart zurückgesetzt)
# ═══════════════════════════════════════════════════════════════════════

class WalkingPadSpeedSensor(WalkingPadSensorBase):
    """Aktuelle Geschwindigkeit."""

    _attr_name = "Geschwindigkeit"
    _attr_device_class = SensorDeviceClass.SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_icon = "mdi:speedometer"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_speed"

    @property
    def native_value(self) -> float | None:
        """Aktuelle Geschwindigkeit in km/h."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("speed", 0), 1)
        return 0.0


class WalkingPadStepsSensor(WalkingPadSensorBase):
    """Schritte in der aktuellen Session."""

    _attr_name = "Schritte (Session)"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "Schritte"
    _attr_icon = "mdi:shoe-print"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_steps"

    @property
    def native_value(self) -> int:
        """Aktuelle Schrittzahl der Session."""
        if self.coordinator.data:
            return int(self.coordinator.data.get("steps", 0))
        return 0


class WalkingPadDistanceSensor(WalkingPadSensorBase):
    """Distanz in der aktuellen Session."""

    _attr_name = "Distanz (Session)"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:map-marker-distance"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_distance"

    @property
    def native_value(self) -> float:
        """Aktuelle Distanz der Session in km."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("distance", 0), 2)
        return 0.0


class WalkingPadTimeSensor(WalkingPadSensorBase):
    """Aktive Zeit der Session."""

    _attr_name = "Zeit (Session)"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:timer-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_time"

    @property
    def native_value(self) -> int:
        """Aktive Zeit in Sekunden."""
        if self.coordinator.data:
            return int(self.coordinator.data.get("time", 0))
        return 0


class WalkingPadCaloriesSensor(WalkingPadSensorBase):
    """Kalorien in der aktuellen Session."""

    _attr_name = "Kalorien (Session)"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_CALORIE
    _attr_icon = "mdi:fire"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_calories"

    @property
    def native_value(self) -> int:
        """Kalorien der Session."""
        if self.coordinator.data:
            return int(self.coordinator.data.get("calories", 0))
        return 0


class WalkingPadStatusSensor(WalkingPadSensorBase):
    """Status des Bands."""

    _attr_name = "Status"
    _attr_icon = "mdi:information-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self) -> str:
        """Aktueller Status."""
        if not self.coordinator.data:
            return "unavailable"
        belt_state = self.coordinator.data.get("belt_state", 0)
        is_running = self.coordinator.data.get("is_running", False)
        speed = self.coordinator.data.get("speed", 0)

        states = {
            0: "Bereit",
            1: "Läuft",
            2: "Pause",
            3: "Stop",
        }
        # Fallback: Wenn speed > 0 aber belt_state nicht 1, trotzdem "Läuft"
        if is_running and belt_state != 1:
            return "Läuft"
        return states.get(belt_state, "Unbekannt")

    @property
    def icon(self) -> str:
        """Dynamisches Icon."""
        if not self.coordinator.data:
            return "mdi:help-circle-outline"
        is_running = self.coordinator.data.get("is_running", False)
        belt_state = self.coordinator.data.get("belt_state", 0)

        if is_running or belt_state == 1:
            return "mdi:run-fast"
        icons = {
            0: "mdi:power-standby",
            2: "mdi:pause-circle-outline",
            3: "mdi:stop-circle-outline",
        }
        return icons.get(belt_state, "mdi:help-circle-outline")


# ═══════════════════════════════════════════════════════════════════════
# Gesamt-Statistik Sensoren (persistent über Neustarts mit RestoreEntity)
# ═══════════════════════════════════════════════════════════════════════

class WalkingPadTotalSensorBase(CoordinatorEntity, RestoreEntity, SensorEntity):
    """Basisklasse für persistente Gesamt-Sensoren."""

    def __init__(
        self,
        coordinator: WalkingPadCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialisiert den Sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = _device_info(entry)
        self._total_value: float = 0.0  # Wird wiederhergestellt
        self._last_session_value: float = 0.0  # Letzter Wert vom Gerät

    async def async_added_to_hass(self) -> None:
        """Wird aufgerufen wenn die Entity zu HA hinzugefügt wird."""
        await super().async_added_to_hass()
        # Letzten gespeicherten Wert wiederherstellen
        if (last_state := await self.async_get_last_state()) is not None:
            try:
                self._total_value = float(last_state.state)
                _LOGGER.info("%s: Wert wiederhergestellt: %s", self.entity_id, self._total_value)
            except (ValueError, TypeError):
                _LOGGER.warning("%s: Konnte Wert nicht wiederherstellen: %s",
                               self.entity_id, last_state.state)
                self._total_value = 0.0
        else:
            _LOGGER.info("%s: Kein gespeicherter Wert gefunden, starte bei 0", self.entity_id)

    def _calculate_total(self, session_value: float) -> float:
        """
        Berechnet den Gesamt-Wert.
        Erkennt wenn das Gerät zurückgesetzt wurde (Session-Wert kleiner als vorher).
        """
        # Reset erkannt? (Session-Wert ist kleiner als der letzte)
        if session_value < self._last_session_value:
            # Vorherige Session zum Gesamt-Wert addieren
            self._total_value += self._last_session_value
            _LOGGER.info("%s: Reset erkannt, Gesamt-Wert jetzt: %s",
                        self.entity_id, self._total_value)

        self._last_session_value = session_value
        return self._total_value + session_value


class WalkingPadTotalStepsSensor(WalkingPadTotalSensorBase):
    """Schritte GESAMT (persistent über Neustarts)."""

    _attr_name = "Schritte (Gesamt)"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = "Schritte"
    _attr_icon = "mdi:shoe-print"
    _attr_entity_category = None  # Haupt-Entity, nicht Diagnostik

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_total_steps"

    @property
    def native_value(self) -> int:
        """Gesamte Schrittzahl."""
        if self.coordinator.data:
            session_steps = float(self.coordinator.data.get("steps", 0))
            return int(self._calculate_total(session_steps))
        return int(self._total_value)


class WalkingPadTotalDistanceSensor(WalkingPadTotalSensorBase):
    """Distanz GESAMT in km (persistent über Neustarts)."""

    _attr_name = "Distanz (Gesamt)"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:map-marker-distance"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_total_distance"

    @property
    def native_value(self) -> float:
        """Gesamte Distanz in km."""
        if self.coordinator.data:
            session_distance = float(self.coordinator.data.get("distance", 0))
            return round(self._calculate_total(session_distance), 2)
        return round(self._total_value, 2)


class WalkingPadTotalCaloriesSensor(WalkingPadTotalSensorBase):
    """Kalorien GESAMT (persistent, berechnet aus Gesamt-Distanz)."""

    _attr_name = "Kalorien (Gesamt)"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_CALORIE
    _attr_icon = "mdi:fire"

    # ~60 kcal pro km beim Gehen
    KCAL_PER_KM = 60

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_total_calories"

    @property
    def native_value(self) -> int:
        """Gesamte Kalorien (berechnet aus Gesamt-Distanz)."""
        if self.coordinator.data:
            total_distance = self.coordinator.data.get("total_distance", 0)
            return int(total_distance * self.KCAL_PER_KM)
        return int(self._total_value * self.KCAL_PER_KM)

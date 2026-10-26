"""Number Entity für WalkingPad Geschwindigkeit."""

from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfSpeed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MIN_SPEED, MAX_SPEED, SPEED_STEP
from .coordinator import WalkingPadCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setzt die Number Entity ein."""
    coordinator: WalkingPadCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WalkingPadSpeedNumber(coordinator, entry)])


class WalkingPadSpeedNumber(CoordinatorEntity, NumberEntity):
    """Number Entity für die Geschwindigkeit."""

    _attr_name = "Geschwindigkeit"
    _attr_unique_id_suffix = "speed_control"
    _attr_native_min_value = MIN_SPEED
    _attr_native_max_value = MAX_SPEED
    _attr_native_step = SPEED_STEP
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:speedometer"

    def __init__(
        self,
        coordinator: WalkingPadCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialisiert die Number Entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_speed_control"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get("name", "WalkingPad"),
            manufacturer="KingSmith",
            model="WalkingPad",
        )

    @property
    def native_value(self) -> float | None:
        """Aktuelle Geschwindigkeit."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("speed", 0), 1)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Setzt die Geschwindigkeit."""
        await self.coordinator.async_set_speed(value)

"""Switch für WalkingPad - Band an/aus."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
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
    """Setzt den Switch ein."""
    coordinator: WalkingPadCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WalkingPadPowerSwitch(coordinator, entry)])


class WalkingPadPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch zum Starten/Stoppen des Bands."""

    _attr_name = "WalkingPad"
    _attr_icon = "mdi:treadmill"

    def __init__(
        self,
        coordinator: WalkingPadCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialisiert den Switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_power"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get("name", "WalkingPad"),
            manufacturer="KingSmith",
            model="WalkingPad",
        )

    @property
    def is_on(self) -> bool | None:
        """Ist das Band an?"""
        if self.coordinator.data:
            return self.coordinator.data.get("is_running", False)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Startet das Band."""
        await self.coordinator.async_start_belt()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stoppt das Band."""
        await self.coordinator.async_stop_belt()

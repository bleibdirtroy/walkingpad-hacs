"""Buttons für WalkingPad - Speed Presets."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WalkingPadCoordinator

SPEED_PRESETS = [
    ("Langsam", 1.0, "mdi:tortoise"),
    ("Gehen", 2.0, "mdi:walk"),
    ("Walking", 3.0, "mdi:run"),
    ("Joggen", 4.0, "mdi:run-fast"),
    ("Schnell", 5.0, "mdi:speedometer-medium"),
    ("Max", 6.0, "mdi:speedometer-slow"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setzt die Buttons ein."""
    coordinator: WalkingPadCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        WalkingPadSpeedPresetButton(coordinator, entry, name, speed, icon)
        for name, speed, icon in SPEED_PRESETS
    ]

    async_add_entities(entities)


class WalkingPadSpeedPresetButton(CoordinatorEntity, ButtonEntity):
    """Button für Geschwindigkeits-Presets."""

    def __init__(
        self,
        coordinator: WalkingPadCoordinator,
        entry: ConfigEntry,
        preset_name: str,
        speed: float,
        icon: str,
    ) -> None:
        """Initialisiert den Button."""
        super().__init__(coordinator)
        self._entry = entry
        self._speed = speed
        self._attr_name = f"Speed {speed:.1f} km/h ({preset_name})"
        self._attr_unique_id = f"{entry.entry_id}_speed_{int(speed * 10)}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get("name", "WalkingPad"),
            manufacturer="KingSmith",
            model="WalkingPad",
        )

    async def async_press(self) -> None:
        """Setzt die voreingestellte Geschwindigkeit."""
        await self.coordinator.async_set_speed(self._speed)

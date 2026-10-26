"""Buttons für WalkingPad - Start/Stop, Speed Presets und Modi."""

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
    ("Max", 6.0, "mdi:speedometer"),
]

MODES = [
    ("Auto", 0, "mdi:robot"),
    ("Manuell", 1, "mdi:hand-back-left"),
    ("Standby", 2, "mdi:power-standby"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setzt die Buttons ein."""
    coordinator: WalkingPadCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        # Start/Stop Buttons
        WalkingPadStartButton(coordinator, entry),
        WalkingPadStopButton(coordinator, entry),
    ]

    # Speed Presets
    entities.extend([
        WalkingPadSpeedPresetButton(coordinator, entry, name, speed, icon)
        for name, speed, icon in SPEED_PRESETS
    ])

    # Modus-Wechsel Buttons
    entities.extend([
        WalkingPadModeButton(coordinator, entry, name, mode, icon)
        for name, mode, icon in MODES
    ])

    async_add_entities(entities)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    """Erstellt die Device Info."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.data.get("name", "WalkingPad"),
        manufacturer="KingSmith",
        model="WalkingPad",
    )


class WalkingPadStartButton(CoordinatorEntity, ButtonEntity):
    """Button zum Starten des Bands."""

    _attr_name = "Start"
    _attr_icon = "mdi:play-circle"

    def __init__(self, coordinator: WalkingPadCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_start"
        self._attr_device_info = _device_info(entry)

    async def async_press(self) -> None:
        """Startet das Band."""
        await self.coordinator.async_start_belt()


class WalkingPadStopButton(CoordinatorEntity, ButtonEntity):
    """Button zum Stoppen des Bands."""

    _attr_name = "Stop"
    _attr_icon = "mdi:stop-circle"

    def __init__(self, coordinator: WalkingPadCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_stop"
        self._attr_device_info = _device_info(entry)

    async def async_press(self) -> None:
        """Stoppt das Band."""
        await self.coordinator.async_stop_belt()


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
        super().__init__(coordinator)
        self._entry = entry
        self._speed = speed
        self._attr_name = f"Speed {speed:.1f} km/h ({preset_name})"
        self._attr_unique_id = f"{entry.entry_id}_speed_{int(speed * 10)}"
        self._attr_icon = icon
        self._attr_device_info = _device_info(entry)

    async def async_press(self) -> None:
        """Setzt die voreingestellte Geschwindigkeit."""
        await self.coordinator.async_set_speed(self._speed)


class WalkingPadModeButton(CoordinatorEntity, ButtonEntity):
    """Button zum Wechseln des Modus (Auto/Manuell/Standby)."""

    def __init__(
        self,
        coordinator: WalkingPadCoordinator,
        entry: ConfigEntry,
        mode_name: str,
        mode: int,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._mode = mode
        self._attr_name = f"Modus: {mode_name}"
        self._attr_unique_id = f"{entry.entry_id}_mode_{mode}"
        self._attr_icon = icon
        self._attr_device_info = _device_info(entry)

    async def async_press(self) -> None:
        """Wechselt den Modus."""
        await self.coordinator.async_switch_mode(self._mode)

"""WalkingPad Integration für Home Assistant."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_NAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from ph4_walkingpad.pad import Controller

from .const import (
    DOMAIN,
    SERVICE_SET_SPEED,
    SERVICE_START,
    SERVICE_STOP,
    ATTR_SPEED,
)
from .coordinator import WalkingPadCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.BUTTON,
]

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setzt die WalkingPad Integration ein."""
    address = entry.data[CONF_ADDRESS]
    name = entry.data.get(CONF_NAME, "WalkingPad")

    coordinator = WalkingPadCoordinator(hass, address, name)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Services registrieren
    await _async_register_services(hass)

    # Plattformen laden
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entlädt die Integration sauber."""
    coordinator: WalkingPadCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Verbindung trennen
    await coordinator.async_disconnect()

    # Plattformen entladen
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_register_services(hass: HomeAssistant) -> None:
    """Registriert die Services."""

    async def handle_start(call: ServiceCall) -> None:
        """Startet das Band."""
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.async_start_belt()

    async def handle_stop(call: ServiceCall) -> None:
        """Stoppt das Band."""
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.async_stop_belt()

    async def handle_set_speed(call: ServiceCall) -> None:
        """Setzt die Geschwindigkeit."""
        speed = call.data[ATTR_SPEED]
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.async_set_speed(speed)

    hass.services.async_register(DOMAIN, SERVICE_START, handle_start)
    hass.services.async_register(DOMAIN, SERVICE_STOP, handle_stop)
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SPEED,
        handle_set_speed,
        schema=vol.Schema({vol.Required(ATTR_SPEED): vol.Coerce(float)}),
    )

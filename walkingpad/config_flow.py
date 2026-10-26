"""Config Flow für WalkingPad."""

import logging
from typing import Any

import voluptuous as vol
from bleak import BleakScanner
from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_NAME, DEFAULT_SCAN_TIMEOUT

_LOGGER = logging.getLogger(__name__)


async def _async_find_device(hass, address: str | None = None) -> dict[str, Any] | None:
    """Findet ein WalkingPad Gerät."""
    # 1. Versuche gespeicherte/übergebene Adresse
    if address:
        try:
            dev = await BleakScanner.find_device_by_address(address, timeout=5)
            if dev:
                return {"address": dev.address, "name": dev.name or DEFAULT_NAME}
        except Exception:
            pass

    # 2. Scanne nach Name
    try:
        dev = await BleakScanner.find_device_by_name("WalkingPad", timeout=DEFAULT_SCAN_TIMEOUT)
        if dev:
            return {"address": dev.address, "name": dev.name or DEFAULT_NAME}
    except Exception:
        pass

    # 3. Fallback: Alle Geräte scannen
    try:
        devices = await BleakScanner.discover(timeout=DEFAULT_SCAN_TIMEOUT, return_adv=True)
        for addr, (dev, adv) in devices.items():
            if dev.name and "walkingpad" in dev.name.lower():
                return {"address": dev.address, "name": dev.name}
    except Exception:
        pass

    return None


class WalkingPadConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für WalkingPad."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialisiert den Flow."""
        self._discovered_devices: dict[str, dict[str, Any]] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Erster Schritt: Automatische Erkennung oder manuelle Eingabe."""
        errors = {}

        if user_input is not None:
            address = user_input.get(CONF_ADDRESS)
            name = user_input.get(CONF_NAME, DEFAULT_NAME)

            # Prüfe ob Adresse schon konfiguriert
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=name,
                data={CONF_ADDRESS: address, CONF_NAME: name},
            )

        # Automatisch suchen
        device = await _async_find_device(self.hass)

        if device:
            # Gerät gefunden - automatisch konfigurieren
            await self.async_set_unique_id(device["address"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=device["name"],
                data={CONF_ADDRESS: device["address"], CONF_NAME: device["name"]},
            )

        # Manuelle Eingabe
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ADDRESS): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }),
            errors=errors,
            description_placeholders={"info": "Gib die MAC-Adresse deines WalkingPad ein (z.B. AA:BB:CC:DD:EE:FF). Du findest sie mit 'bluetoothctl scan on' oder in der offiziellen App."},
        )

    async def async_step_bluetooth(
        self, discovery_info: dict[str, Any]
    ) -> FlowResult:
        """Bluetooth Auto-Discovery."""
        address = discovery_info["address"]
        name = discovery_info.get("name", DEFAULT_NAME)

        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        self.context["title_placeholders"] = {"name": name}

        return self.async_create_entry(
            title=name,
            data={CONF_ADDRESS: address, CONF_NAME: name},
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "WalkingPadOptionsFlow":
        """Options Flow."""
        return WalkingPadOptionsFlow(config_entry)


class WalkingPadOptionsFlow(config_entries.OptionsFlow):
    """Options Flow für WalkingPad."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialisiert den Options Flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Verwaltet die Optionen."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init")

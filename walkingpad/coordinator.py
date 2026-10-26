"""DataUpdateCoordinator für WalkingPad."""

import asyncio
import logging
from datetime import timedelta
from typing import Any

from bleak import BleakScanner
from bleak.exc import BleakError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from ph4_walkingpad.pad import Controller, WalkingPad, WalkingPadCurStatus

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class WalkingPadCoordinator(DataUpdateCoordinator):
    """Koordiniert die Bluetooth-Verbindung zum WalkingPad."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
        name: str,
    ) -> None:
        """Initialisiert den Coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{name}",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.address = address
        self.device_name = name
        self.controller: Controller | None = None
        self._connected = False
        self._lock = asyncio.Lock()

    async def _async_setup(self) -> None:
        """Verbindet beim Setup."""
        await self._async_connect()

    async def _async_connect(self) -> bool:
        """Verbindet mit dem WalkingPad."""
        try:
            self.controller = Controller()
            await self.controller.run(self.address)
            self.controller.on_cur_status_received = self._on_status
            await self.controller.switch_mode(WalkingPad.MODE_MANUAL)
            await asyncio.sleep(0.5)
            self._connected = True
            _LOGGER.info("Verbunden mit WalkingPad: %s (%s)", self.device_name, self.address)
            return True
        except Exception as err:
            _LOGGER.error("Verbindungsfehler: %s", err)
            self._connected = False
            return False

    def _on_status(self, sender, status: WalkingPadCurStatus) -> None:
        """Callback für Status-Updates vom Gerät."""
        # Wird im BLE-Thread aufgerufen, daher nur Daten speichern
        self._last_status = status

    async def _async_update_data(self) -> dict[str, Any]:
        """Holt aktuelle Daten vom WalkingPad."""
        if not self._connected or not self.controller:
            # Versuche neu zu verbinden
            if not await self._async_connect():
                raise UpdateFailed("Keine Verbindung zum WalkingPad")

        try:
            # Status explizit anfragen
            await self.controller.ask_stats()
            await asyncio.sleep(0.3)

            # Letzten Status holen
            status = getattr(self.controller, "last_status", None) or getattr(self, "_last_status", None)

            if status is None:
                raise UpdateFailed("Keine Status-Daten empfangen")

            # Daten extrahieren
            data = {
                "speed": status.speed / 10.0,  # km/h
                "steps": status.steps,
                "distance": status.dist / 100.0,  # km
                "time": status.time,  # Sekunden
                "belt_state": status.belt_state,
                "mode": status.manual_mode,
                "is_running": status.belt_state == 1,
                "calories": round(status.dist / 100.0 * 60),  # ~60 kcal/km
            }

            self._connected = True
            return data

        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen der Daten: %s", err)
            self._connected = False
            raise UpdateFailed(f"Fehler: {err}") from err

    async def async_start_belt(self) -> None:
        """Startet das Band."""
        if not self.controller or not self._connected:
            raise RuntimeError("Nicht verbunden")
        await self.controller.start_belt()
        await self.async_request_refresh()

    async def async_stop_belt(self) -> None:
        """Stoppt das Band."""
        if not self.controller or not self._connected:
            raise RuntimeError("Nicht verbunden")
        await self.controller.stop_belt()
        await self.async_request_refresh()

    async def async_set_speed(self, speed_kmh: float) -> None:
        """Setzt die Geschwindigkeit in km/h."""
        if not self.controller or not self._connected:
            raise RuntimeError("Nicht verbunden")
        # Auf 0.5 Schritte runden
        speed_kmh = round(speed_kmh * 2) / 2
        speed_kmh = max(0.5, min(6.0, speed_kmh))
        await self.controller.change_speed(int(speed_kmh * 10))
        await self.async_request_refresh()

    async def async_disconnect(self) -> None:
        """Trennt die Verbindung sauber."""
        if self.controller and self._connected:
            try:
                await self.controller.stop_belt()
                await asyncio.sleep(0.3)
                await self.controller.disconnect()
                _LOGGER.info("Verbindung getrennt")
            except Exception as err:
                _LOGGER.warning("Fehler beim Trennen: %s", err)
        self._connected = False

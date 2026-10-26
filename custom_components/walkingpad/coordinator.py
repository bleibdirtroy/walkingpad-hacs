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

# Belt States vom WalkingPad
BELT_STATE_STANDBY = 0
BELT_STATE_RUNNING = 1
BELT_STATE_PAUSED = 2
BELT_STATE_STOPPED = 3


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
        self._last_status: WalkingPadCurStatus | None = None

        # Für Gesamt-Statistik: letzte Werte vom Gerät
        self._last_device_steps: int | None = None
        self._last_device_distance: float | None = None
        # Akkumulierte Werte (werden von Sensoren aktualisiert)
        self.total_steps_offset: int = 0
        self.total_distance_offset: float = 0.0

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
        """Callback für Status-Updates vom Gerät (läuft im BLE-Thread)."""
        self._last_status = status
        _LOGGER.debug(
            "Status empfangen: steps=%s dist=%s speed=%s belt_state=%s",
            status.steps, status.dist, status.speed, status.belt_state
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Holt aktuelle Daten vom WalkingPad."""
        if not self._connected or not self.controller:
            # Versuche neu zu verbinden
            if not await self._async_connect():
                raise UpdateFailed("Keine Verbindung zum WalkingPad")

        try:
            # Alten Status merken für Vergleich
            old_status = self._last_status

            # Status explizit anfragen
            await self.controller.ask_stats()
            # Länger warten damit die Antwort kommt (mindestens 1 Sekunde)
            await asyncio.sleep(1.0)

            # Aktuellen Status holen (vom Controller oder Callback)
            status = getattr(self.controller, "last_status", None) or self._last_status

            if status is None:
                raise UpdateFailed("Keine Status-Daten empfangen")

            # Prüfen ob sich was geändert hat
            if old_status and status.rtime == old_status.rtime:
                # Gleicher Status - trotzdem Daten zurückgeben
                _LOGGER.debug("Status unverändert")

            # Rohwerte vom Gerät
            device_steps = status.steps
            device_distance = status.dist / 100.0  # km
            device_speed = status.speed / 10.0  # km/h
            belt_state = status.belt_state

            # Gesamt-Statistik berechnen:
            # Wenn das Gerät neu gestartet wurde (steps kleiner als vorher),
            # addieren wir den letzten Wert zum Offset
            if self._last_device_steps is not None:
                if device_steps < self._last_device_steps:
                    # Gerät wurde zurückgesetzt - zur Gesamt-Statistik addieren
                    self.total_steps_offset += self._last_device_steps
                    _LOGGER.info("Schritt-Reset erkannt: +%s Schritte zur Gesamt-Statistik",
                                self._last_device_steps)
                if device_distance < self._last_device_distance:
                    # Distanz wurde zurückgesetzt
                    self.total_distance_offset += self._last_device_distance
                    _LOGGER.info("Distanz-Reset erkannt: +%.2f km zur Gesamt-Statistik",
                                self._last_device_distance)

            self._last_device_steps = device_steps
            self._last_device_distance = device_distance

            # Gesamt-Werte berechnen
            total_steps = self.total_steps_offset + device_steps
            total_distance = round(self.total_distance_offset + device_distance, 2)

            # Daten zusammenstellen (nur echte Werte vom Gerät!)
            data = {
                # Aktuelle Session (vom Gerät)
                "speed": device_speed,
                "steps": device_steps,
                "distance": device_distance,
                "time": status.time,
                "belt_state": belt_state,
                "mode": status.manual_mode,
                # Status: läuft wenn belt_state == 1 ODER speed > 0
                "is_running": belt_state == BELT_STATE_RUNNING or device_speed > 0,
                # Gesamt-Werte (persistent über Neustarts)
                "total_steps": total_steps,
                "total_distance": total_distance,
                # Für Debugging
                "total_steps_offset": self.total_steps_offset,
                "total_distance_offset": self.total_distance_offset,
            }

            _LOGGER.debug(
                "Daten: steps=%s (gesamt=%s) dist=%.2f (gesamt=%.2f) speed=%.1f running=%s",
                device_steps, total_steps, device_distance, total_distance,
                device_speed, data["is_running"]
            )

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
        await asyncio.sleep(0.5)
        await self.async_request_refresh()

    async def async_stop_belt(self) -> None:
        """Stoppt das Band."""
        if not self.controller or not self._connected:
            raise RuntimeError("Nicht verbunden")
        await self.controller.stop_belt()
        await asyncio.sleep(0.5)
        await self.async_request_refresh()

    async def async_set_speed(self, speed_kmh: float) -> None:
        """Setzt die Geschwindigkeit in km/h."""
        if not self.controller or not self._connected:
            raise RuntimeError("Nicht verbunden")
        # Auf 0.5 Schritte runden
        speed_kmh = round(speed_kmh * 2) / 2
        speed_kmh = max(0.5, min(6.0, speed_kmh))
        await self.controller.change_speed(int(speed_kmh * 10))
        await asyncio.sleep(0.3)
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

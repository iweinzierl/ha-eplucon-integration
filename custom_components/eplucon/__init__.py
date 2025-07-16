"""The Eplucon Heat Pump integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .eplucon_api import EpluconAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eplucon from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create API instance
    api = EpluconAPI(
        email=entry.data["email"],
        password=entry.data["password"]
    )

    # Create data update coordinator
    coordinator = EpluconDataUpdateCoordinator(
        hass=hass,
        api=api,
        scan_interval=timedelta(minutes=entry.data.get("scan_interval", 1))
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up all platforms for this device/service
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class EpluconDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Eplucon API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: EpluconAPI,
        scan_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # Login to Eplucon if needed
            if not self.api.is_authenticated:
                await self.api.login()

            # Fetch heat pump data
            data = await self.api.get_heat_pump_data()
            return data
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}")

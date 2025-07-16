"""Platform for Eplucon heat pump sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eplucon sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    for sensor_type, sensor_config in SENSOR_TYPES.items():
        entities.append(
            EpluconSensor(
                coordinator=coordinator,
                sensor_type=sensor_type,
                config=sensor_config,
                config_entry=config_entry,
            )
        )

    async_add_entities(entities, True)


class EpluconSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Eplucon heat pump sensor."""

    def __init__(
        self,
        coordinator,
        sensor_type: str,
        config: dict,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._sensor_type = sensor_type
        self._config = config
        self._config_entry = config_entry
        
        # Set up entity attributes
        self._attr_name = config["name"]  # Keep original friendly name
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_icon = config["icon"]
        
        # Set entity_id with eplucon prefix for the actual entity ID
        self.entity_id = f"sensor.eplucon_{sensor_type}"
        
        # Set up device class and unit
        if config.get("device_class"):
            if config["device_class"] == "temperature":
                self._attr_device_class = SensorDeviceClass.TEMPERATURE
                self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
                self._attr_state_class = SensorStateClass.MEASUREMENT
            else:
                self._attr_device_class = config["device_class"]
        
        if config.get("unit"):
            self._attr_native_unit_of_measurement = config["unit"]

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Eplucon Heat Pump",
            "manufacturer": "Eplucon",
            "model": "Heat Pump",
            "sw_version": "1.0",
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        
        return self.coordinator.data.get(self._sensor_type)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self._sensor_type in self.coordinator.data
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}
        
        if self.coordinator.data:
            attrs["last_update"] = self.coordinator.last_update_success
            
            # Add some debug information
            if self.coordinator.data.get("raw_data"):
                attrs["raw_value"] = self.coordinator.data["raw_data"].get(self._sensor_type)
        
        return attrs

"""Constants for the Eplucon integration."""

DOMAIN = "eplucon"

# Configuration keys
CONF_EMAIL = "email"
CONF_PASSWORD = "password" 
CONF_SCAN_INTERVAL = "scan_interval"

# Default values
DEFAULT_SCAN_INTERVAL = 1  # minutes
MIN_SCAN_INTERVAL = 1  # minimum 1 minute
MAX_SCAN_INTERVAL = 60  # maximum 60 minutes

# Sensor types and their properties
SENSOR_TYPES = {
    "supply_temperature_1": {
        "name": "Supply Water Temperature 1",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "supply_temperature_2": {
        "name": "Supply Water Temperature 2",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "source_temperature_1": {
        "name": "Source Temperature 1",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "source_temperature_2": {
        "name": "Source Temperature 2",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "outdoor_temperature": {
        "name": "Outdoor Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "inside_temperature": {
        "name": "Inside Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "inside_configured_temperature": {
        "name": "Inside Configured Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "hot_water_temperature": {
        "name": "Hot Water Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "hot_water_configured_temperature": {
        "name": "Hot Water Configured Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "power_consumption": {
        "name": "Power Consumption",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
    },
    "energy_delivered": {
        "name": "Energy Delivered",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
    },
    "cop": {
        "name": "Coefficient of Performance (SPF)",
        "unit": None,
        "icon": "mdi:gauge",
        "device_class": None,
    },
    "operation_mode": {
        "name": "Operation Mode",
        "unit": None,
        "icon": "mdi:heat-pump",
        "device_class": None,
    },
    "heating_mode_status": {
        "name": "Heating Mode Status",
        "unit": None,
        "icon": "mdi:power",
        "device_class": None,
    },
    "dhw_status": {
        "name": "DHW Status",
        "unit": None,
        "icon": "mdi:water-boiler",
        "device_class": None,
    },
    "dg1_status": {
        "name": "DG1 Status",
        "unit": None,
        "icon": "mdi:radiator",
        "device_class": None,
    },
}

# API endpoints based on actual Eplucon portal
EPLUCON_BASE_URL = "https://portaal.eplucon.de"
LOGIN_ENDPOINT = "/login"
DATA_ENDPOINT = "/e-control/ajax/graphicsdata"

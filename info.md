# Eplucon Heat Pump Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/iweinzierl/ha-eplucon-integration.svg)](https://github.com/iweinzierl/ha-eplucon-integration/releases)
[![GitHub Downloads](https://img.shields.io/github/downloads/iweinzierl/ha-eplucon-integration/total.svg)](https://github.com/iweinzierl/ha-eplucon-integration/releases)

A Home Assistant integration for Eplucon heat pumps that provides real-time monitoring of temperatures, energy consumption, and operational status.

## Features

- **Temperature Monitoring**: Supply, source, outdoor, indoor, and hot water temperatures
- **Energy Tracking**: Power consumption and energy delivered
- **Performance Metrics**: COP (Coefficient of Performance) monitoring
- **Operational Status**: Heat pump mode, heating status, and DGS information
- **Automatic Authentication**: Handles session management and re-authentication
- **Real-time Updates**: Configurable refresh intervals (default: 1 minute)

## Supported Devices

This integration works with Eplucon heat pumps that are accessible through the [Eplucon Portal](https://portaal.eplucon.de).

## Installation

### Via HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Search for "Eplucon Heat Pump" in HACS
3. Download and install the integration
4. Restart Home Assistant
5. Add the integration through Settings → Devices & Services

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/iweinzierl/ha-eplucon-integration/releases)
2. Extract to `custom_components/eplucon/` in your Home Assistant config directory
3. Restart Home Assistant
4. Add the integration through Settings → Devices & Services

## Configuration

The integration can be configured through the Home Assistant UI:

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Eplucon Heat Pump"
4. Enter your Eplucon portal credentials:
   - **Email**: Your Eplucon portal email address
   - **Password**: Your Eplucon portal password
   - **Scan Interval**: Update frequency in minutes (default: 1)

## Available Sensors

The integration provides the following sensors with `eplucon_` entity ID prefix:

### Temperature Sensors
- Supply Temperature 1 & 2 (`sensor.eplucon_supply_temperature_1`)
- Source Temperature 1 & 2 (`sensor.eplucon_source_temperature_1`)
- Outdoor Temperature (`sensor.eplucon_outdoor_temperature`)
- Indoor Temperature (`sensor.eplucon_inside_temperature`)
- Indoor Configured Temperature (`sensor.eplucon_inside_configured_temperature`)
- Hot Water Temperature (`sensor.eplucon_hot_water_temperature`)
- Hot Water Configured Temperature (`sensor.eplucon_hot_water_configured_temperature`)

### Energy & Performance
- Power Consumption (`sensor.eplucon_power_consumption`)
- Energy Delivered (`sensor.eplucon_energy_delivered`)
- COP - Coefficient of Performance (`sensor.eplucon_cop`)

### Status Information
- Operation Mode (`sensor.eplucon_operation_mode`)
- Heating Mode Status (`sensor.eplucon_heating_mode_status`)
- DHW Status (`sensor.eplucon_dhw_status`)
- DG1 Status (`sensor.eplucon_dg1_status`)

## Troubleshooting

### Common Issues

**Sensors showing as unavailable:**
- Check your Eplucon portal credentials
- Verify your heat pump is accessible through the portal
- Check Home Assistant logs for authentication errors

**No data updates:**
- Ensure your internet connection is stable
- Check if the Eplucon portal is accessible
- Verify the scan interval isn't too aggressive

**Authentication failures:**
- Double-check your email and password
- Try logging into the Eplucon portal manually
- Check for any account restrictions

### Debug Logging

To enable debug logging, add this to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.eplucon: debug
```

## Support

- [Report Issues](https://github.com/iweinzierl/ha-eplucon-integration/issues)
- [Feature Requests](https://github.com/iweinzierl/ha-eplucon-integration/issues)
- [Discussions](https://github.com/iweinzierl/ha-eplucon-integration/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

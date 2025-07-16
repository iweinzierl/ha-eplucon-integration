# Eplucon Heat Pump Integration for Home Assistant

This custom integration allows Home Assistant to monitor heat pump data from Eplucon's website by scraping the manufacturer's official web portal.

## Features

- **Temperature Monitoring**: Monitor various water temperatures including:
  - Supply water temperature
  - Return water temperature  
  - Hot water temperature
  - Outdoor temperature
- **Status Monitoring**: Track heat pump operational status
- **Performance Metrics**: Monitor Coefficient of Performance (COP)
- **Configurable Polling**: Set scan interval from 1 to 60 minutes (minimum 1 minute as requested)
- **Secure Authentication**: Uses your personal Eplucon account credentials

## Installation

### Requirements

- Home Assistant 2023.1.0 or later
- Python dependencies: `aiohttp`, `beautifulsoup4` (automatically installed)

### Manual Installation

#### Step 1: Locate your Home Assistant configuration directory

Your Home Assistant configuration directory contains the `configuration.yaml` file. The location depends on your installation method:

- **Home Assistant OS/Supervised**: `/config/` (accessible via File Editor add-on or Samba share)
- **Home Assistant Container**: The directory you mapped to `/config` in your Docker run command
- **Home Assistant Core**: Usually `~/.homeassistant/` or the directory where you installed Home Assistant
- **HassBoot**: Check your `docker-compose.yml` for the volume mapping

#### Step 2: Create the custom_components folder

1. **Create the custom_components folder** (if it doesn't exist):
   - Navigate to your Home Assistant configuration directory (where `configuration.yaml` is located)
   - Create a folder named `custom_components` if it doesn't already exist
   
2. **Install the integration**:
   - Copy the entire `custom_components/eplucon` folder from this repository
   - Place it inside your Home Assistant `custom_components` directory
   - Your folder structure should look like this:
     ```
     homeassistant/
     ├── configuration.yaml
     ├── custom_components/
     │   └── eplucon/
     │       ├── __init__.py
     │       ├── config_flow.py
     │       ├── const.py
     │       ├── eplucon_api.py
     │       ├── sensor.py
     │       ├── manifest.json
     │       └── translations/
     │           ├── en.json
     │           └── de.json
     ```

#### Step 3: Complete installation

1. **Restart Home Assistant**
2. Go to **Settings** > **Devices & Services** > **Integrations**
3. Click **Add Integration** and search for "Eplucon Heat Pump"

### HACS Installation

This integration can be added to HACS as a custom repository:

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots in the top right corner
4. Select **Custom repositories**
5. Add this repository URL and select **Integration** as the category
6. Install the integration
7. Restart Home Assistant

## Configuration

1. Navigate to **Settings** > **Devices & Services** > **Integrations**
2. Click **Add Integration** and search for "Eplucon Heat Pump"
3. Enter your configuration:
   - **Email Address**: Your Eplucon account email
   - **Password**: Your Eplucon account password
   - **Scan Interval**: How often to fetch data (1-60 minutes, default: 1 minute)

## Sensors

The integration creates the following sensors based on the actual data from your Eplucon heat pump:

### Temperature Sensors
| Sensor | Description | Unit | Device Class |
|--------|-------------|------|--------------|
| `sensor.eplucon_supply_temperature_1` | Supply water temperature 1 | °C | Temperature |
| `sensor.eplucon_supply_temperature_2` | Supply water temperature 2 | °C | Temperature |
| `sensor.eplucon_source_temperature_1` | Source temperature 1 | °C | Temperature |
| `sensor.eplucon_source_temperature_2` | Source temperature 2 | °C | Temperature |
| `sensor.eplucon_outdoor_temperature` | Outdoor temperature | °C | Temperature |
| `sensor.eplucon_inside_temperature` | Inside temperature | °C | Temperature |
| `sensor.eplucon_inside_configured_temperature` | Inside configured temperature | °C | Temperature |
| `sensor.eplucon_hot_water_temperature` | Hot water temperature | °C | Temperature |
| `sensor.eplucon_hot_water_configured_temperature` | Hot water configured temperature | °C | Temperature |

### Energy & Performance
| Sensor | Description | Unit | Device Class |
|--------|-------------|------|--------------|
| `sensor.eplucon_power_consumption` | Power consumption | kWh | Energy |
| `sensor.eplucon_energy_delivered` | Energy delivered | kWh | Energy |
| `sensor.eplucon_cop` | Coefficient of Performance (SPF) | - | - |

### Status Information
| Sensor | Description | Unit | Device Class |
|--------|-------------|------|--------------|
| `sensor.eplucon_operation_mode` | Operation mode (e.g., Cooling/Heating) | - | - |
| `sensor.eplucon_heating_mode_status` | Heating mode status | - | - |
| `sensor.eplucon_dhw_status` | Domestic hot water status | - | - |
| `sensor.eplucon_dg1_status` | Heating zone 1 status | - | - |

## API Implementation Notes

This integration is designed to work with Eplucon's website. The current implementation includes:

- **Web Scraping**: Parses HTML content from the Eplucon web portal
- **Session Management**: Maintains login session with automatic re-authentication
- **Error Handling**: Robust error handling for connection and authentication issues
- **Data Validation**: Validates temperature ranges and data integrity

### Customization Required

The web scraping logic in `eplucon_api.py` will need to be customized based on the actual HTML structure of Eplucon's website. Key areas to modify:

1. **Login Process**: Update form field names and authentication flow
2. **Data Extraction**: Modify HTML parsing logic to match actual page structure  
3. **API Endpoints**: Update URLs to match actual Eplucon endpoints
4. **Data Mapping**: Adjust sensor data extraction based on available information

## Development

### Project Structure

```
custom_components/eplucon/
├── __init__.py              # Integration setup and coordinator
├── config_flow.py          # Configuration flow for UI setup
├── const.py                # Constants and configuration
├── eplucon_api.py          # API client for Eplucon website
├── sensor.py               # Sensor platform implementation  
├── manifest.json           # Integration metadata
└── translations/           # UI translations
    ├── en.json             # English translations
    └── de.json             # German translations
```

### Key Components

- **EpluconAPI**: Handles authentication and data scraping
- **EpluconDataUpdateCoordinator**: Manages periodic data updates
- **EpluconSensor**: Individual sensor entities for each data point
- **ConfigFlow**: User-friendly configuration interface

## Security Considerations

- Credentials are stored securely in Home Assistant's configuration
- Sessions are properly managed with automatic cleanup
- No credentials are logged or exposed in debug output
- Uses HTTPS for all communications with Eplucon

## Troubleshooting

### Common Issues

1. **Authentication Fails**: Verify email and password are correct
2. **"Verbindung zur Eplucon-Website fehlgeschlagen" / Connection Failed**: 
   - This usually means the account module index couldn't be extracted after successful login
   - The integration has successfully authenticated but can't find the data access key
   - Try setting up the integration again
   - Check the Home Assistant logs for more details
3. **"Authenticated but could not extract account_module_index"**: 
   - The login succeeded but the integration can't find the required data access key
   - This may happen if Eplucon changed their website structure
   - Check for a debug file `login_response_debug.html` in your logs
4. **No Data**: Check if Eplucon website structure has changed
5. **Connection Errors**: Verify internet connectivity and Eplucon website availability

### Testing the Integration

You can test the integration separately using the standalone script:

```bash
# Test with your credentials
python3 eplucon_api_standalone.py your-email@example.com your-password
```

This will show detailed logging and help identify where the issue occurs.

### Debug Mode

Enable debug logging by adding this to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.eplucon: debug
```

### Getting Help

If you encounter the "account_module_index" error:

1. Enable debug logging (see above)
2. Try setting up the integration again
3. Check the Home Assistant logs for the specific error message
4. If available, check for a debug file that shows the login response structure
5. Report the issue with the log details (remove any personal information)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This integration is not officially supported by Eplucon. Use at your own risk and ensure compliance with Eplucon's terms of service.

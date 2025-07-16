# Eplucon API Implementation

## Overview

This project now includes a complete implementation for retrieving heat pump data from the Eplucon portal (https://portaal.eplucon.de). The implementation handles:

- **Authentication**: Login to the Eplucon portal using email/password with CSRF token handling
- **Session Management**: Maintains authenticated sessions and handles session expiration
- **Data Retrieval**: Fetches heat pump data from the `/e-control/ajax/graphicsdata` endpoint
- **Data Parsing**: Extracts temperature, energy, and status data from the HTML response

## Data Points Extracted

The integration retrieves the following data points from your heat pump:

### Temperature Sensors
- **Supply Temperature 1 & 2** (`aanvoer-1`, `aanvoer-2`): Water supply temperatures
- **Source Temperature 1 & 2** (`bron-1`, `bron-2`): Heat source temperatures  
- **Outdoor Temperature** (`buitentemp`): Outside air temperature
- **Inside Temperature** (`binnen temp.`): Current indoor temperature
- **Inside Configured Temperature** (`ingestelde binnen temp.`): Target indoor temperature
- **Hot Water Temperature** (`W.W. temperatuur.`): Current hot water storage temperature
- **Hot Water Configured Temperature** (`W.W. temperatuur. ingesteld`): Target hot water temperature

### Energy & Performance
- **Power Consumption** (`Opgenomen vermogen`): Energy consumed (kWh)
- **Energy Delivered** (`Geleverde energie`): Energy delivered by heat pump (kWh)
- **COP/SPF** (`SPF`): Seasonal Performance Factor (efficiency rating)

### Status Information
- **Operation Mode** (`operation-mode`): Current operation mode (e.g., "Kühlung" for cooling)
- **Heating Mode Status** (`heating-mode`): Whether heating is active
- **DHW Status** (`dhw`): Domestic Hot Water status (ON/OFF)
- **DG1 Status** (`dg1`): Heating zone 1 status (ON/OFF)

## Testing the Implementation

### 1. Test Data Parsing (Local)

Test the data parsing functionality with the sample data:

```bash
cd /path/to/ha-eplucon-addon
python3 test_parsing.py
```

This will parse the sample `graphicsdata.json` file and show all extracted data points.

### 2. Test Live API Connection

Test the complete authentication and data retrieval process:

```bash
cd /path/to/ha-eplucon-addon
python3 eplucon_api_standalone.py your-email@example.com your-password
```

This will:
1. Authenticate with the Eplucon portal
2. Extract the `account_module_index` needed for data requests
3. Fetch live heat pump data
4. Display all retrieved sensor values

**Note**: Replace `your-email@example.com` and `your-password` with your actual Eplucon portal credentials.

### 3. Home Assistant Integration

The integration can be installed as a custom component in Home Assistant:

1. Copy the `custom_components/eplucon/` folder to your Home Assistant config
2. Restart Home Assistant
3. Add the integration via the UI or configuration.yaml
4. Provide your Eplucon portal credentials

## Files Updated

### Core Implementation
- `custom_components/eplucon/eplucon_api.py` - Main API client with authentication and data parsing
- `custom_components/eplucon/const.py` - Updated constants and sensor definitions for all data points

### Testing & Examples
- `eplucon_api_standalone.py` - Standalone test script for the API
- `test_parsing.py` - Data parsing validation script
- `example/graphicsdata.json` - Sample data from the portal (anonymized)
- `example/Eplucon_Login.html` - Sample login page structure

## Implementation Details

### Authentication Flow
1. GET `/login` to retrieve CSRF token from `_token` input field
2. POST `/login` with credentials and CSRF token
3. Extract `account_module_index` from response (needed for data requests)
4. Use session cookies for subsequent requests

### Data Endpoint
- URL: `https://portaal.eplucon.de/e-control/ajax/graphicsdata?account_module_index=<index>`
- Returns JSON with `html` field containing the heat pump dashboard HTML
- HTML is parsed to extract temperature, energy, and status values

### Error Handling
- Authentication failures with proper error messages
- Session expiration detection and automatic re-authentication
- Network error handling with retry logic
- Data validation and reasonable range checking

## Next Steps

The implementation is ready for use. You can:

1. Test the standalone API script with your credentials
2. Install the Home Assistant integration
3. Monitor your heat pump data in real-time
4. Create automations based on temperature and efficiency data

If you encounter any issues during testing, the scripts provide detailed logging and will save debug information to help troubleshoot authentication or data parsing problems.

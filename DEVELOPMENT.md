# Eplucon Heat Pump Integration - Development Guide

## Setup for Development

### 1. Development Environment Setup

```bash
# Create virtual environment  
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip first
pip install --upgrade pip

# Install only essential dependencies (avoiding compilation issues)
pip install aiohttp beautifulsoup4 voluptuous

# Or install from requirements-dev.txt
pip install -r requirements-dev.txt
```

#### ✅ macOS Compilation Issues - SOLVED

The original requirements.txt contained the full Home Assistant installation which requires compilation of native extensions. This has been resolved by:

1. **Simplified Requirements**: Only essential packages (aiohttp, beautifulsoup4, voluptuous)
2. **Standalone Testing**: Use `eplucon_api_standalone.py` for API testing without Home Assistant
3. **No Compilation Needed**: All required packages are pure Python or have pre-built wheels

#### Quick Test

```bash
# Test that the environment is working
python -c "import aiohttp, bs4; print('✅ All dependencies installed successfully')"
```

### 2. Installation in Home Assistant

Copy the integration to your Home Assistant custom_components directory:

```bash
# If developing locally
cp -r custom_components/eplucon /path/to/homeassistant/custom_components/

# Or create symlink for development
ln -s $(pwd)/custom_components/eplucon /path/to/homeassistant/custom_components/eplucon
```

### 3. Home Assistant Configuration

Add to your `configuration.yaml` for comprehensive debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.eplucon: debug
    custom_components.eplucon.eplucon_api: debug
    custom_components.eplucon.sensor: debug
    aiohttp.client: debug
```

**Enhanced Logging Features:**
- 🔍 **Detailed Request/Response Logging**: All HTTP requests and responses are logged with status codes, headers, and content lengths
- 💾 **Debug File Generation**: Critical pages saved to `/tmp/` for manual inspection:
  - `/tmp/eplucon_login_page_debug.html` - The login form page
  - `/tmp/eplucon_login_response_debug.html` - Response after login submission
  - `/tmp/eplucon_page_X_debug.html` - Dashboard pages during navigation
  - `/tmp/eplucon_data_response_debug.html` - Heat pump data response
- 🔍 **Pattern Matching Details**: Shows which regex patterns are tested and which ones match
- 📊 **Data Extraction Logging**: Details about each step of HTML parsing and data normalization
- ⚡ **Error Context**: Full tracebacks and error context for debugging connection issues

### 4. Testing the Integration

1. Restart Home Assistant
2. Go to Configuration > Integrations
3. Click "Add Integration"
4. Search for "Eplucon Heat Pump"
5. Enter your Eplucon credentials

## Customizing for Actual Eplucon Website

The current implementation is a template that needs to be adapted to the actual Eplucon website structure. Here's what you'll need to modify:

### 1. Update API Endpoints in `const.py`

```python
# Update these URLs to match actual Eplucon endpoints
EPLUCON_BASE_URL = "https://actual-eplucon-url.com"
LOGIN_ENDPOINT = "/actual/login/path"
DATA_ENDPOINT = "/actual/data/endpoint"
```

### 2. Modify Login Logic in `eplucon_api.py`

Update the `login()` method:
- Inspect the actual login form on Eplucon's website
- Update form field names (might be 'username' instead of 'email')
- Handle any CSRF tokens or additional security measures
- Update success detection logic

### 3. Update Data Scraping in `eplucon_api.py`

Modify the `_parse_html_data()` method:
- Inspect the actual data page HTML structure
- Update CSS selectors and parsing logic
- Map the actual data fields to sensor types

### 4. Add/Remove Sensors in `const.py`

Update `SENSOR_TYPES` based on what data is actually available:

```python
SENSOR_TYPES = {
    # Add/remove based on actual available data
    "actual_sensor_name": {
        "name": "Display Name",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
}
```

## Debugging Steps

### 1. Network Inspection

Use browser developer tools to inspect the actual Eplucon website:
1. Open the Eplucon login page in your browser
2. Open Developer Tools (F12)
3. Go to Network tab
4. Login to your account
5. Look at the network requests to understand:
   - Login endpoint and form data
   - Data endpoints after login
   - Required headers and cookies

### 2. HTML Structure Analysis

After logging in manually:
1. Right-click on temperature values and "Inspect Element"
2. Note the HTML structure and CSS classes
3. Update the parsing logic accordingly

### 3. API Testing Without Home Assistant

Use the standalone API tester to develop and debug the Eplucon integration:

```bash
# Run the standalone API test
python eplucon_api_standalone.py
```

This will:
- Prompt for your Eplucon credentials  
- Test the login process
- Attempt to fetch heat pump data
- Save debug files (debug_login_response.html, debug_data_response.html)
- Show detailed progress and error messages

**Features of the standalone tester:**
- 🔍 **Debug output**: Detailed logging of each step
- 💾 **Response saving**: HTML responses saved for analysis  
- 🔧 **Mock data**: Creates sample data if real data isn't found
- 📊 **Data validation**: Tests the data normalization process

## File Structure Overview

```
custom_components/eplucon/
├── __init__.py              # Main integration setup
├── config_flow.py          # Configuration UI
├── const.py                # Constants (UPDATE URLS HERE)
├── eplucon_api.py          # API client (UPDATE PARSING HERE)
├── sensor.py               # Sensor entities
├── manifest.json           # Integration metadata
└── translations/           # UI translations
    ├── en.json
    └── de.json
```

## Next Steps

1. **Analyze Eplucon Website**: Study the actual website structure
2. **Update Constants**: Modify URLs and endpoints in `const.py`
3. **Adapt Login**: Update authentication logic in `eplucon_api.py`
4. **Fix Data Parsing**: Modify HTML parsing to match actual structure
5. **Test Integration**: Test with real credentials and data
6. **Refine Sensors**: Add/remove sensors based on available data
7. **Error Handling**: Add specific error handling for Eplucon's responses

## Security Notes

- Never commit real credentials to version control
- Use environment variables or a local config file for testing
- Ensure HTTPS is used for all communications
- Handle session timeouts gracefully
- Implement rate limiting to avoid overwhelming the Eplucon server

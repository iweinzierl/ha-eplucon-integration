"""API client for Eplucon heat pump data."""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any, Dict
from urllib.parse import urlencode

import aiohttp
from bs4 import BeautifulSoup

from .const import EPLUCON_BASE_URL, LOGIN_ENDPOINT, DATA_ENDPOINT

_LOGGER = logging.getLogger(__name__)


class EpluconAuthError(Exception):
    """Exception to indicate authentication failure."""


class EpluconConnectionError(Exception):
    """Exception to indicate connection failure."""


class EpluconAPI:
    """API client for Eplucon heat pump data."""

    def __init__(self, email: str, password: str) -> None:
        """Initialize the API client."""
        self.email = email
        self.password = password
        self.session: aiohttp.ClientSession | None = None
        self.is_authenticated = False
        self._account_module_index: str | None = None
        
        # Test logging levels
        _LOGGER.error("🔴 ERROR: Eplucon API initialized")
        _LOGGER.warning("🟡 WARNING: Eplucon API initialized")
        _LOGGER.info("🔵 INFO: Eplucon API initialized")
        _LOGGER.debug("🟢 DEBUG: Eplucon API initialized")

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure we have an active session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            )
        return self.session

    async def login(self) -> bool:
        """Login to Eplucon portal."""
        _LOGGER.error("🔴 STARTING LOGIN PROCESS")  # Using ERROR level to ensure visibility
        session = await self._ensure_session()
        
        try:
            # First, get the login page to extract CSRF token
            login_url = f"{EPLUCON_BASE_URL}{LOGIN_ENDPOINT}"
            _LOGGER.error(f"🔴 Attempting to load login page: {login_url}")
            
            async with session.get(login_url) as response:
                _LOGGER.error(f"🔴 Login page response status: {response.status}")
                _LOGGER.debug(f"Login page response headers: {dict(response.headers)}")
                
                if response.status != 200:
                    raise EpluconConnectionError(f"Failed to load login page: {response.status}")
                
                login_page_content = await response.text()
                _LOGGER.error(f"🔴 Login page content length: {len(login_page_content)} characters")
                
                # Parse the login page first
                try:
                    soup = BeautifulSoup(login_page_content, 'html.parser')
                except Exception as e:
                    _LOGGER.error(f"Failed to parse login page HTML: {e}")
                    raise EpluconConnectionError(f"Failed to parse login page: {e}")
                
                # Log login page structure for debugging
                try:
                    _LOGGER.debug(f"Login page contains {len(re.findall(r'<input', login_page_content))} input fields")
                    _LOGGER.debug(f"Login page forms: {len(soup.find_all('form'))}")
                    if soup.find('input', {'name': '_token'}):
                        _LOGGER.debug("CSRF token field found in login page")
                    else:
                        _LOGGER.debug("No CSRF token field found in login page")
                except Exception as e:
                    _LOGGER.debug(f"Error analyzing login page structure: {e}")
                
                # Extract CSRF token
                csrf_token = None
                token_input = soup.find('input', {'name': '_token'})
                if token_input:
                    csrf_token = token_input.get('value')
                    _LOGGER.error("🔴 Found CSRF token in login form")
                else:
                    _LOGGER.error("🔴 No CSRF token found in login form")
                    # Try alternative token field names
                    alt_tokens = ['csrf_token', 'authenticity_token', 'token']
                    for token_name in alt_tokens:
                        token_input = soup.find('input', {'name': token_name})
                        if token_input:
                            csrf_token = token_input.get('value')
                            _LOGGER.error(f"🔴 Found alternative token field: {token_name}")
                            break
                
                if not csrf_token:
                    _LOGGER.error("Could not find any CSRF token on login page")
                    # List all input fields for debugging
                    all_inputs = soup.find_all('input')
                    _LOGGER.debug(f"All input fields found: {[(inp.get('name'), inp.get('type')) for inp in all_inputs]}")
                    raise EpluconAuthError("Could not find CSRF token on login page")

                # Prepare login form data
                form_data = {
                    '_token': csrf_token,
                    'username': self.email,
                    'password': self.password,
                }
                _LOGGER.error(f"🔴 Prepared login form data with fields: {list(form_data.keys())}")

            # Submit login form
            _LOGGER.error(f"🔴 Submitting login form to: {login_url}")
            async with session.post(login_url, data=form_data, allow_redirects=True) as response:
                _LOGGER.error(f"🔴 Login form submission response status: {response.status}")
                _LOGGER.debug(f"Login response headers: {dict(response.headers)}")
                _LOGGER.error(f"🔴 Final URL after redirects: {response.url}")
                
                if response.status == 200:
                    response_text = await response.text()
                    _LOGGER.error(f"🔴 Login response content length: {len(response_text)} characters")
                    
                    # Log login response structure for debugging
                    _LOGGER.debug(f"Login response contains: forms={len(BeautifulSoup(response_text, 'html.parser').find_all('form'))}")
                    _LOGGER.debug(f"Login response URL path: {response.url.path}")
                    _LOGGER.debug(f"Login response title: {BeautifulSoup(response_text, 'html.parser').find('title')}")
                    
                    # Log first 500 chars of response (without sensitive data)
                    safe_response = re.sub(r'password["\']?\s*[:=]\s*["\'][^"\']*["\']', 'password: [REDACTED]', response_text[:500])
                    safe_response = re.sub(r'email["\']?\s*[:=]\s*["\'][^"\']*["\']', 'email: [REDACTED]', safe_response)
                    _LOGGER.debug(f"Login response snippet: {safe_response}")
                    
                    # Log potential success/error indicators
                    error_indicators = ["error", "invalid", "failed", "denied"]
                    found_errors = [err for err in error_indicators if err in response_text.lower()]
                    if found_errors:
                        _LOGGER.warning(f"Error indicators found in response: {found_errors}")
                    
                    # Check if login was successful - look for dashboard indicators
                    success_indicators = ["e-control", "heat pump", "dashboard", "logout", "heatpump"]
                    found_indicators = [indicator for indicator in success_indicators if indicator in response_text.lower()]
                    _LOGGER.info(f"Success indicators found: {found_indicators}")
                    
                    if found_indicators:
                        self.is_authenticated = True
                        _LOGGER.info("Login appears successful based on page content indicators")
                        
                        # Navigate directly to heatpump page to find the account_module_index
                        _LOGGER.error("🔴 Navigating to heatpump page to find account_module_index")
                        await self._find_module_index_from_heatpump_page(session)
                        
                        return True
                    else:
                        _LOGGER.error("Login failed - no success indicators found in response")
                        # Check for error messages in the response
                        try:
                            soup = BeautifulSoup(response_text, 'html.parser')
                            error_divs = soup.find_all('div', class_=['alert-danger', 'error', 'alert-error'])
                            error_messages = [div.get_text(strip=True) for div in error_divs if div.get_text(strip=True)]
                            if error_messages:
                                _LOGGER.error(f"Found error messages: {error_messages}")
                                raise EpluconAuthError(f"Login failed with errors: {'; '.join(error_messages)}")
                            else:
                                _LOGGER.error("No specific error messages found, but login appears to have failed")
                                raise EpluconAuthError("Invalid credentials or login failed")
                        except Exception as parse_error:
                            _LOGGER.debug(f"Could not parse error messages from response: {parse_error}")
                            raise EpluconAuthError("Invalid credentials or login failed")
                else:
                    _LOGGER.error(f"Login failed with HTTP status: {response.status}")
                    response_text = await response.text()
                    _LOGGER.debug(f"Error response content: {response_text[:500]}...")
                    raise EpluconConnectionError(f"Login failed with status: {response.status}")
                    
        except aiohttp.ClientError as err:
            raise EpluconConnectionError(f"Connection error during login: {err}")
        except Exception as err:
            _LOGGER.error("Unexpected error during login: %s", err)
            raise EpluconConnectionError(f"Unexpected error: {err}")

    async def get_heat_pump_data(self) -> Dict[str, Any]:
        """Fetch heat pump data from Eplucon portal."""
        _LOGGER.error("🔴 === Starting heat pump data retrieval ===")
        
        if not self.is_authenticated:
            _LOGGER.error("🔴 Not authenticated, attempting login first")
            await self.login()

        _LOGGER.error(f"🔴 Account Module Index: {self._account_module_index}")
        if not self._account_module_index:
            # Try to re-authenticate and find the module index
            _LOGGER.error("🔴 No account module index available, attempting re-authentication")
            self.is_authenticated = False
            await self.login()
            
            if not self._account_module_index:
                _LOGGER.error("🔴 Could not obtain account module index after re-authentication")
                raise EpluconConnectionError("Could not obtain account module index needed for data access. Please check your credentials and ensure you have access to the heat pump data.")

        session = await self._ensure_session()
        
        try:
            # Construct the graphicsdata URL with the account module index
            params = {'account_module_index': self._account_module_index}
            data_url = f"{EPLUCON_BASE_URL}{DATA_ENDPOINT}?{urlencode(params)}"
            _LOGGER.error(f"🔴 Fetching data from: {data_url}")
            
            # Add headers that might be expected for AJAX requests
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': f"{EPLUCON_BASE_URL}/e-control/heatpump"
            }
            _LOGGER.debug(f"Using headers: {headers}")
            
            async with session.get(data_url, headers=headers) as response:
                _LOGGER.error(f"🔴 Data request response status: {response.status}")
                _LOGGER.debug(f"Data response headers: {dict(response.headers)}")
                
                if response.status == 401 or response.status == 403:
                    # Session expired, try to re-authenticate
                    _LOGGER.warning("Session expired (401/403), attempting re-authentication")
                    self.is_authenticated = False
                    await self.login()
                    
                    # Retry with new session
                    params = {'account_module_index': self._account_module_index}
                    data_url = f"{EPLUCON_BASE_URL}{DATA_ENDPOINT}?{urlencode(params)}"
                    _LOGGER.info(f"Retrying data fetch after re-auth: {data_url}")
                    async with session.get(data_url, headers=headers) as retry_response:
                        if retry_response.status != 200:
                            _LOGGER.error(f"Failed to fetch data after re-auth: {retry_response.status}")
                            raise EpluconConnectionError(f"Failed to fetch data after re-auth: {retry_response.status}")
                        response = retry_response
                elif response.status != 200:
                    _LOGGER.error(f"Failed to fetch data: {response.status}")
                    response_text = await response.text()
                    _LOGGER.debug(f"Error response content: {response_text[:500]}...")
                    raise EpluconConnectionError(f"Failed to fetch data: {response.status}")

                # Parse JSON response containing HTML
                _LOGGER.error("🔴 Parsing response data")
                content_type = response.headers.get('content-type', '')
                _LOGGER.error(f"🔴 Response content type: {content_type}")
                
                try:
                    if 'application/json' in content_type:
                        json_data = await response.json()
                        _LOGGER.error(f"🔴 JSON response keys: {list(json_data.keys())}")
                        html_content = json_data.get('html', '')
                    elif 'text/html' in content_type:
                        # The endpoint returned HTML directly instead of JSON
                        _LOGGER.warning("Data endpoint returned HTML instead of JSON - this might indicate authentication issues or wrong endpoint")
                        html_content = await response.text()
                        _LOGGER.info(f"Direct HTML response length: {len(html_content)} characters")
                        
                        # Check if this is actually the login page or an error page
                        if any(indicator in html_content.lower() for indicator in ["login", "sign in", "password", "username"]):
                            _LOGGER.error("Received login page instead of data - session may have expired")
                            raise EpluconConnectionError("Session expired - received login page instead of data")
                        
                        # Check if this is an error page
                        if any(indicator in html_content.lower() for indicator in ["error", "access denied", "forbidden", "not found", "klant", "customer"]):
                            _LOGGER.error("Received error/customer page instead of data")
                            soup_error = BeautifulSoup(html_content, 'html.parser')
                            error_title = soup_error.find('title')
                            error_msg = error_title.get_text(strip=True) if error_title else "Unknown error"
                            
                            # This suggests we need to find the correct module index
                            _LOGGER.error(f"Data request failed with: {error_msg}")
                            _LOGGER.error("This usually means the account_module_index is missing or incorrect")
                            
                            raise EpluconConnectionError(f"Data request failed: {error_msg} - account_module_index may be incorrect")
                    else:
                        _LOGGER.error(f"Unexpected content type: {content_type}")
                        response_text = await response.text()
                        _LOGGER.debug(f"Response content: {response_text[:500]}...")
                        raise EpluconConnectionError(f"Unexpected content type: {content_type}")
                        
                except Exception as e:
                    if "Invalid JSON response" in str(e):
                        raise  # Re-raise our own exceptions
                    _LOGGER.error(f"Failed to parse response: {e}")
                    response_text = await response.text()
                    _LOGGER.debug(f"Response content: {response_text[:500]}...")
                    raise EpluconConnectionError(f"Failed to parse response: {e}")
                
                _LOGGER.info(f"HTML content length: {len(html_content)} characters")
                
                if not html_content:
                    _LOGGER.error("No HTML content found in JSON response")
                    _LOGGER.debug(f"Full JSON response: {json_data}")
                    raise EpluconConnectionError("No HTML content found in response")

                # Log data response structure instead of saving file
                _LOGGER.debug(f"Data response content type: {response.headers.get('content-type', 'unknown')}")
                try:
                    soup_preview = BeautifulSoup(html_content, 'html.parser')
                    _LOGGER.debug(f"HTML content has {len(soup_preview.find_all('div'))} div elements")
                    _LOGGER.debug(f"HTML content snippet: {html_content[:200]}...")
                except Exception as e:
                    _LOGGER.debug(f"Could not parse HTML preview: {e}")
                    _LOGGER.debug(f"Raw HTML snippet: {html_content[:200]}...")

                # Parse the HTML data to extract sensor values
                _LOGGER.info("Parsing HTML data to extract sensor values")
                data = self._parse_html_data(html_content)
                _LOGGER.info(f"Extracted {len(data)} raw data points: {list(data.keys())}")
                
                normalized_data = self._normalize_data(data)
                _LOGGER.info(f"Normalized to {len(normalized_data)} valid data points: {list(normalized_data.keys())}")
                
                return normalized_data
                
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Connection error while fetching data: {err}")
            raise EpluconConnectionError(f"Connection error while fetching data: {err}")
        except Exception as err:
            _LOGGER.error(f"Unexpected error while fetching data: {err}")
            import traceback
            _LOGGER.debug(f"Data fetch traceback: {traceback.format_exc()}")
            raise

    def _parse_html_data(self, html_content: str) -> Dict[str, Any]:
        """Parse heat pump data from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        data = {}
        
        # Extract temperature values from pointer elements
        pointers = soup.find_all('div', class_='pointer')
        for pointer in pointers:
            data_type = pointer.get('data-type', '')
            text = pointer.get_text(strip=True)
            
            if data_type == 'aanvoer-1':
                data['supply_temperature_1'] = self._extract_temperature(text)
            elif data_type == 'aanvoer-2':
                data['supply_temperature_2'] = self._extract_temperature(text)
            elif data_type == 'bron-1':
                data['source_temperature_1'] = self._extract_temperature(text)
            elif data_type == 'bron-2':
                data['source_temperature_2'] = self._extract_temperature(text)
            elif data_type == 'buitentemp':
                data['outdoor_temperature'] = self._extract_temperature(text)
            elif data_type == 'binnen temp.':
                data['inside_temperature'] = self._extract_temperature(text)
            elif data_type == 'ingestelde binnen temp. ':
                data['inside_configured_temperature'] = self._extract_temperature(text)
            elif data_type == 'W.W. temperatuur.':
                data['hot_water_temperature'] = self._extract_temperature(text)
            elif data_type == 'W.W. temperatuur. ingesteld':
                data['hot_water_configured_temperature'] = self._extract_temperature(text)
            elif data_type == 'Opgenomen vermogen':
                data['power_consumption'] = self._extract_energy(text)
            elif data_type == 'Geleverde energie':
                data['energy_delivered'] = self._extract_energy(text)
            elif data_type == 'SPF':
                data['cop'] = self._extract_float(text)
        
        # Extract operation mode
        operation_mode_elem = soup.find('div', class_='element operation-mode')
        if operation_mode_elem:
            data['operation_mode'] = operation_mode_elem.get_text(strip=True)
        
        # Extract heating mode status
        heating_mode_elem = soup.find('div', class_='element heating-mode')
        if heating_mode_elem:
            title = heating_mode_elem.get('title', '')
            data['heating_mode_status'] = title.strip()
        
        # Extract DGS status information
        dgs_elem = soup.find('div', class_='element dgs')
        if dgs_elem:
            spans = dgs_elem.find_all('span')
            for span in spans:
                span_text = span.get_text(strip=True)
                classes = span.get('class', [])
                status = 'ON' if 'on' in classes else 'OFF'
                
                if span_text == 'dhw':
                    data['dhw_status'] = status
                elif span_text == 'dg1':
                    data['dg1_status'] = status
        
        # Extract inside temperature from element class
        inside_temp_elem = soup.find('div', class_='element inside-temp')
        if inside_temp_elem and 'inside_temperature' not in data:
            data['inside_temperature'] = self._extract_temperature(inside_temp_elem.get_text(strip=True))
        
        # Extract configured inside temperature from element class
        inside_config_elem = soup.find('div', class_='element inside-configured-temp')
        if inside_config_elem and 'inside_configured_temperature' not in data:
            data['inside_configured_temperature'] = self._extract_temperature(inside_config_elem.get_text(strip=True))
        
        return data

    def _extract_temperature(self, text: str) -> float | None:
        """Extract temperature value from text."""
        # Look for temperature patterns like "25.5°C" or "25.5 °C"
        match = re.search(r'(-?\d+\.?\d*)\s*°?C?', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None

    def _extract_energy(self, text: str) -> float | None:
        """Extract energy value from text (kWh)."""
        # Look for energy patterns like "45 kWh"
        match = re.search(r'(\d+\.?\d*)\s*kWh', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None

    def _extract_float(self, text: str) -> float | None:
        """Extract float value from text."""
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None

    def _normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate the data."""
        normalized = {}
        
        # Temperature sensors - validate reasonable ranges
        temp_sensors = [
            'supply_temperature_1', 'supply_temperature_2',
            'source_temperature_1', 'source_temperature_2',
            'outdoor_temperature', 'inside_temperature',
            'inside_configured_temperature', 'hot_water_temperature',
            'hot_water_configured_temperature'
        ]
        
        for key in temp_sensors:
            value = raw_data.get(key)
            if value is not None and isinstance(value, (int, float)):
                if -50 <= value <= 100:  # Reasonable temperature range
                    normalized[key] = value
        
        # Energy sensors
        energy_sensors = ['power_consumption', 'energy_delivered']
        for key in energy_sensors:
            value = raw_data.get(key)
            if value is not None and isinstance(value, (int, float)):
                if 0 <= value <= 100000:  # Reasonable energy range
                    normalized[key] = value
        
        # COP/SPF
        cop_value = raw_data.get('cop')
        if cop_value is not None and isinstance(cop_value, (int, float)):
            if 0 <= cop_value <= 20:  # Reasonable COP range
                normalized['cop'] = cop_value
        
        # Status values
        status_keys = ['operation_mode', 'heating_mode_status', 'dhw_status', 'dg1_status']
        for key in status_keys:
            value = raw_data.get(key)
            if value is not None:
                normalized[key] = str(value)
        
        return normalized

    async def close(self) -> None:
        """Close the API session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
        self.is_authenticated = False
        self._account_module_index = None

    async def _find_module_index_from_heatpump_page(self, session: aiohttp.ClientSession) -> None:
        """Find the account_module_index by browsing to the heatpump page."""
        try:
            _LOGGER.error("🔴 === Finding module index from heatpump page ===")
            
            # Navigate directly to the heatpump page
            heatpump_url = f"{EPLUCON_BASE_URL}/e-control/heatpump"
            _LOGGER.error(f"🔴 Loading heatpump page: {heatpump_url}")
            
            async with session.get(heatpump_url) as response:
                _LOGGER.error(f"🔴 Heatpump page response status: {response.status}")
                _LOGGER.error(f"🔴 Final URL after redirects: {response.url}")
                
                if response.status == 200:
                    content = await response.text()
                    _LOGGER.error(f"🔴 Heatpump page content length: {len(content)} characters")
                    
                    # Search for 32-character hex strings (account_module_index format)
                    hex_32_patterns = re.findall(r'\b([a-f0-9]{32})\b', content)
                    if hex_32_patterns:
                        _LOGGER.error(f"🟢 Found 32-char hex patterns: {hex_32_patterns}")
                        self._account_module_index = hex_32_patterns[0]
                        _LOGGER.error(f"� Using account_module_index: {self._account_module_index}")
                        return
                    
                    # If no 32-char patterns, look for the specific account_module_index parameter
                    module_patterns = [
                        r'account_module_index["\']?\s*[:=]\s*["\']?([a-f0-9]{32})["\']?',
                        r'graphicsdata\?account_module_index=([a-f0-9]{32})',
                        r'data-account-module-index\s*=\s*["\']([a-f0-9]{32})["\']',
                    ]
                    
                    for pattern in module_patterns:
                        match = re.search(pattern, content)
                        if match:
                            self._account_module_index = match.group(1)
                            _LOGGER.error(f"🟢 Found module index with pattern: {self._account_module_index}")
                            return
                    
                    _LOGGER.error("🔴 No 32-character account_module_index found in heatpump page")
                    
                    # Debug: log a snippet of the page to see what's there
                    _LOGGER.debug(f"Heatpump page snippet: {content[:500]}...")
                    
                else:
                    _LOGGER.error(f"🔴 Failed to load heatpump page: HTTP {response.status}")
                    
        except Exception as e:
            _LOGGER.error(f"Error finding module index from heatpump page: {e}")
            import traceback
            _LOGGER.debug(f"Module index search traceback: {traceback.format_exc()}")

# Legacy client class for backwards compatibility
EpluconClient = EpluconAPI

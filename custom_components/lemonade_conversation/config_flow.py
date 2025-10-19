# custom_components/lemonade_conversation/config_flow.py
import voluptuous as vol
import aiohttp
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_API_KEY,
    CONF_MODEL,
    CONF_TEMPERATURE,
    CONF_MAX_TOKENS,
    CONF_VERIFY_SSL,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_VERIFY_SSL
)

class LemonadeConversationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lemonade Conversation."""

    VERSION = 2

    def __init__(self):
        """Initialize the config flow."""
        self._base_url = None
        self._models = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            self._base_url = user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL)
            
            # Validate base URL
            if not self._base_url.startswith(("http://", "https://")):
                errors[CONF_BASE_URL] = "invalid_url"
            elif not self._base_url.endswith("/api/v1/"):
                # Automatically append /api/v1/ if missing
                self._base_url = self._base_url.rstrip("/") + "/api/v1/"
            
            if not errors:
                # Try to fetch available models
                try:
                    models = await self._fetch_models()
                    self._models = models
                    return await self.async_step_model_selection()
                except Exception as ex:
                    errors[CONF_BASE_URL] = "connection_failed"
                    self._base_url = user_input[CONF_BASE_URL]

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                vol.Optional(CONF_API_KEY): str,
                vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
            }),
            errors=errors
        )

    async def async_step_model_selection(self, user_input=None):
        """Handle model selection."""
        errors = {}
        
        if user_input is not None:
            return self.async_create_entry(
                title="Lemonade Conversation",
                data={
                    CONF_BASE_URL: self._base_url,
                    CONF_API_KEY: user_input.get(CONF_API_KEY),
                    CONF_MODEL: user_input.get(CONF_MODEL, DEFAULT_MODEL),
                    CONF_TEMPERATURE: user_input.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
                    CONF_MAX_TOKENS: user_input.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS),
                    CONF_VERIFY_SSL: user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                }
            )

        # Create model selection dropdown
        model_schema = {}
        if self._models:
            model_schema[vol.Required(CONF_MODEL, default=DEFAULT_MODEL)] = vol.In(self._models)
        else:
            model_schema[vol.Required(CONF_MODEL, default=DEFAULT_MODEL)] = str

        return self.async_show_form(
            step_id="model_selection",
            data_schema=vol.Schema({
                **model_schema,
                vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): vol.Coerce(float),
                vol.Optional(CONF_MAX_TOKENS, default=DEFAULT_MAX_TOKENS): vol.Coerce(int),
                vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
                vol.Optional(CONF_API_KEY): str,
            }),
            errors=errors
        )

    async def _fetch_models(self):
        """Fetch available models from Lemonade Server."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._base_url.rstrip('/')}/models",
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Extract model names from the response
                        if isinstance(data, dict) and 'data' in data:
                            return [model.get('id') for model in data.get('data', []) if 'id' in model]
                        elif isinstance(data, list):
                            return [model.get('id') for model in data if 'id' in model]
                        else:
                            return [DEFAULT_MODEL]
                    else:
                        return [DEFAULT_MODEL]
        except Exception:
            return [DEFAULT_MODEL]

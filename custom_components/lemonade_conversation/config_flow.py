# /config/custom_components/lemonade_conversation/config_flow.py

from __future__ import annotations
import logging
from typing import Any

import voluptuous as vol
import aiohttp

from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_MODEL = "local-model"

# ... (La función get_models y la clase LemonadeConfigFlow no cambian, las incluyo por completitud)

async def get_models(hass, base_url: str) -> list[str]:
    """Get list of models from Lemonade server."""
    if not base_url:
        _LOGGER.warning("get_models called with no base_url.")
        return []
    session = async_get_clientsession(hass)
    url = f"{base_url.rstrip('/')}/api/v1/models"
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            data = await response.json()
            return [model["id"] for model in data.get("data", [])]
    except Exception as e:
        _LOGGER.error("Failed to get models from %s: %s", url, e)
        return []

class LemonadeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lemonade Conversation."""
    VERSION = 1
    user_data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            self.user_data = user_input
            return await self.async_step_model()
        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required("base_url", default="http://<IP_LEMONADE_SERVER>:8000"): str,
            vol.Optional("api_key", default=""): str,
        }))

    async def async_step_model(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        models = await get_models(self.hass, self.user_data.get("base_url", ""))
        if not models: models = [DEFAULT_MODEL]
        if user_input is not None:
            final_data = {**self.user_data, **user_input}
            return self.async_create_entry(title="Lemonade Conversation", data=final_data, options={"system_prompt": "Eres un asistente de domótica útil y conciso."})
        suggested_model = "Qwen3-Coder-30B-A3B-Instruct-GGUF"
        default_selection = suggested_model if suggested_model in models else models[0]
        return self.async_show_form(step_id="model", data_schema=vol.Schema({vol.Required("model", default=default_selection): vol.In(models)}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return LemonadeOptionsFlowHandler(config_entry)


# --- ¡AQUÍ ESTÁ LA CLASE CORREGIDA! ---
class LemonadeOptionsFlowHandler(OptionsFlow):
    """Handle an options flow for Lemonade."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Show the main menu for options."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["general", "personality"],
        )

    async def async_step_general(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle general settings, like changing the model."""
        if user_input is not None:
            # La forma moderna usa el .options de la entrada de configuración almacenada
            return self.async_create_entry(title="", data={**self.config_entry.options, **user_input})

        base_url = self.config_entry.data.get("base_url")
        if not base_url:
            return self.async_abort(reason="reconfigure_failed_missing_url")
        
        models = await get_models(self.hass, base_url)
        if not models:
            current_model = self.config_entry.options.get("model", self.config_entry.data.get("model"))
            models = [current_model]

        return self.async_show_form(
            step_id="general",
            data_schema=vol.Schema({
                vol.Required(
                    "model",
                    default=self.config_entry.options.get("model", self.config_entry.data.get("model"))
                ): vol.In(models),
            }),
        )

    async def async_step_personality(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle personality settings, like the system prompt."""
        if user_input is not None:
            return self.async_create_entry(title="", data={**self.config_entry.options, **user_input})

        return self.async_show_form(
            step_id="personality",
            data_schema=vol.Schema({
                vol.Optional(
                    "system_prompt",
                    default=self.config_entry.options.get("system_prompt", "")
                ): TextSelector(TextSelectorConfig(multiline=True)),
            }),
        )

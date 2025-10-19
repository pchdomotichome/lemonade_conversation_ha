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

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_MODEL = "local-model" # Fallback por si no se puede obtener la lista

async def get_models(hass, base_url: str) -> list[str]:
    """Get list of models from Lemonade server."""
    session = async_get_clientsession(hass)
    url = f"{base_url.rstrip('/')}/api/v1/models"
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            data = await response.json()
            # La API devuelve una lista de objetos, extraemos el 'id' de cada uno
            return [model["id"] for model in data.get("data", [])]
    except Exception as e:
        _LOGGER.error("Failed to get models from %s: %s", url, e)
        return []

class LemonadeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lemonade Conversation."""

    VERSION = 1
    
    # Guardaremos los datos del usuario entre pasos
    user_data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step where the user provides the URL."""
        errors = {}
        if user_input is not None:
            self.user_data = user_input
            # Guardamos la URL y vamos al siguiente paso
            return await self.async_step_model()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("base_url", default="http://<IP_LEMONADE_SERVER>:8000"): str,
                vol.Optional("api_key", default=""): str, # API Key ahora es opcional
            }),
            errors=errors,
        )

    async def async_step_model(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the step where the user selects a model."""
        # Obtenemos los modelos desde el servidor del usuario
        models = await get_models(self.hass, self.user_data["base_url"])
        
        if not models:
            # Si no podemos obtener modelos, permitimos que el usuario escriba uno manualmente
            models = [DEFAULT_MODEL]

        if user_input is not None:
            # Combinamos los datos de todos los pasos y creamos la entrada
            final_data = {**self.user_data, **user_input}
            return self.async_create_entry(title="Lemonade Conversation", data=final_data)

        # Pre-seleccionar un modelo si existe en la lista, si no, el primero
        suggested_model = "Qwen3-Coder-30B-A3B-Instruct-GGUF"
        default_selection = suggested_model if suggested_model in models else models[0]

        return self.async_show_form(
            step_id="model",
            data_schema=vol.Schema({
                # Usamos vol.In para crear un dropdown
                vol.Required("model", default=default_selection): vol.In(models),
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return LemonadeOptionsFlowHandler(config_entry)


class LemonadeOptionsFlowHandler(OptionsFlow):
    """Handle an options flow for Lemonade."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Actualiza las opciones y recrea la entrada
            return self.async_create_entry(title="", data=user_input)

        models = await get_models(self.hass, self.config_entry.data["base_url"])
        if not models:
            models = [self.config_entry.options.get("model", DEFAULT_MODEL)]

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    "model",
                    default=self.config_entry.options.get("model", models[0])
                ): vol.In(models),
            }),
        )

# /config/custom_components/lemonade_conversation/config_flow.py

from __future__ import annotations
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Esquema para la configuración inicial
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("api_key"): str,
        # AÑADIMOS ESTE CAMPO PARA LA URL DE TU SERVIDOR
        vol.Required("base_url", default="http://localhost:8000/v1"): str,
    }
)

# Esquema para las opciones (modelo, etc.)
OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional("model", default="local-model"): str,
        # Puedes añadir más opciones aquí en el futuro (temperatura, etc.)
    }
)


class LemonadeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lemonade Conversation."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # Aquí puedes añadir validación si quieres (ej. intentar conectar a la URL)
        
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title="Lemonade Conversation", data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return LemonadeOptionsFlowHandler(config_entry)


class LemonadeOptionsFlowHandler(OptionsFlow):
    """Handle an options flow for Lemonade."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "model",
                        default=self.config_entry.options.get("model", "local-model"),
                    ): str,
                }
            ),
        )

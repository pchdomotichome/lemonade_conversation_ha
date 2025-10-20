# /config/custom_components/lemonade_conversation/conversation.py

import logging
from typing import Literal

# 1. ACTUALIZACIÓN DE LA IMPORTACIÓN
from homeassistant.components.conversation import (
    ConversationEntity,
    ConversationResult,
    ConversationInput, # <-- Añadimos la importación del objeto de entrada
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .conversation_agent import LemonadeAgent

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up conversation entities."""
    async_add_entities([LemonadeConversationEntity(config_entry)])


class LemonadeConversationEntity(ConversationEntity):
    """Lemonade Conversation Agent Entity."""

    _agent: LemonadeAgent | None = None

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_name = "Lemonade Assistant"

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return "*"

    # 2. ACTUALIZACIÓN DE LA FIRMA DE LA FUNCIÓN
    async def async_process(
        self, user_input: ConversationInput # <-- Cambiamos el tipo a ConversationInput
    ) -> ConversationResult:
        """Process a sentence."""
        if self._agent is None:
            self._agent = LemonadeAgent(self.hass, self._entry)

        try:
            # ¡¡LA CORRECCIÓN CLAVE!!
            # Ahora pasamos explícitamente el texto y el id de la conversación.
            agent_response = await self._agent.async_process(
                user_input.text, user_input.conversation_id
            )
            
            response = self.hass.helpers.intent.IntentResponse(self.hass)
            response.async_set_speech(agent_response["response"])

            return ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )
        except Exception as e:
            # Este log es importante si algo más falla
            _LOGGER.exception("Error processing Lemonade conversation")
            response = self.hass.helpers.intent.IntentResponse(self.hass)
            response.async_set_error(
                "intent_error", f"Ocurrió un error inesperado. Revisa los logs de Home Assistant."
            )
            return ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

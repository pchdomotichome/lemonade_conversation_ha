# /config/custom_components/lemonade_conversation/conversation.py

import logging
from typing import Literal

from homeassistant.components.conversation import (
    ConversationEntity,
    ConversationResult,
    ConversationInput,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
# 1. ¡CAMBIO CLAVE EN LA IMPORTACIÓN!
from homeassistant.helpers.intent import IntentResponse

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

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Process a sentence."""
        if self._agent is None:
            self._agent = LemonadeAgent(self.hass, self._entry)

        try:
            agent_response = await self._agent.async_process(
                user_input.text, user_input.conversation_id
            )
            
            # 2. ¡CAMBIO CLAVE EN LA CREACIÓN DE LA RESPUESTA!
            # Creamos la instancia directamente.
            response = IntentResponse(language=user_input.language)
            response.async_set_speech(agent_response["response"])

            return ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )
        except Exception:
            _LOGGER.exception("Error processing Lemonade conversation")
            
            # Corregimos también la respuesta de error.
            response = IntentResponse(language=user_input.language)
            response.async_set_error(
                "intent_error", "Ocurrió un error inesperado al procesar la solicitud."
            )
            return ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

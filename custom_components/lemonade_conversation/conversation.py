# /config/custom_components/lemonade_conversation/conversation.py

import logging
from typing import Literal

# Importación correcta, sin 'ConversationAgent'
from homeassistant.components.conversation import (
    ConversationEntity,
    ConversationResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Importamos la clase que acabamos de mover a su propio archivo
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
        # Este será el nombre que veas en la lista de asistentes
        self._attr_name = "Lemonade Assistant"

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return "*"

    async def async_process(
        self, user_input: str, conversation_id: str | None = None
    ) -> ConversationResult:
        """Process a sentence."""
        if self._agent is None:
            # Creamos la instancia del agente la primera vez que se usa
            self._agent = LemonadeAgent(self.hass, self._entry)

        try:
            agent_response = await self._agent.async_process(user_input, conversation_id)
            
            response = self.hass.helpers.intent.IntentResponse(self.hass)
            response.async_set_speech(agent_response["response"])

            return ConversationResult(
                response=response, conversation_id=conversation_id
            )
        except Exception as e:
            _LOGGER.error("Error processing conversation: %s", e)
            response = self.hass.helpers.intent.IntentResponse(self.hass)
            response.async_set_error(
                "intent_error", f"Lo siento, ocurrió un error: {e}"
            )
            return ConversationResult(
                response=response, conversation_id=conversation_id
            )

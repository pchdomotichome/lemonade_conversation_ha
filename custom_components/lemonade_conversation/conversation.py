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
from homeassistant.helpers.intent import IntentResponse

from .conversation_agent import LemonadeAgent

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up conversation entities."""
    agent = LemonadeAgent(hass, config_entry)
    async_add_entities([LemonadeConversationEntity(agent)])


class LemonadeConversationEntity(ConversationEntity):
    """Lemonade Conversation Agent Entity."""

    def __init__(self, agent: LemonadeAgent) -> None:
        """Initialize the agent."""
        self.agent = agent
        self._attr_unique_id = agent.entry.entry_id
        self._attr_name = "Lemonade Assistant"

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return "*"

    @property
    def has_stream_support(self) -> bool:
        """Return whether the agent supports streaming responses."""
        return self.agent.entry.options.get("stream", False)

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Process a sentence."""
        
        if self.has_stream_support:
            # La respuesta es un generador de IntentResponse, que HA sabe cómo manejar.
            return ConversationResult(
                response=self.agent.async_stream_response(
                    user_input.text, user_input.conversation_id
                ),
                conversation_id=user_input.conversation_id,
            )

        # Lógica sin streaming (ya funciona)
        response_dict = await self.agent.async_process(
            user_input.text, user_input.conversation_id
        )
        response = IntentResponse(language=user_input.language)
        response.async_set_speech(response_dict["response"])
        return ConversationResult(response=response, conversation_id=user_input.conversation_id)

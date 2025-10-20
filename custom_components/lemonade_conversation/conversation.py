# /config/custom_components/lemonade_conversation/conversation.py

import logging
from typing import AsyncGenerator, Literal

from homeassistant.components.conversation import (
    ConversationResult,
    ConversationInput,
    ConversationAgent, # Requerido para el nuevo enfoque
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


class LemonadeConversationEntity(ConversationAgent): # <- CAMBIO: Hereda de ConversationAgent
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

    async def async_process(
        self, user_input: ConversationInput
    ) -> ConversationResult | AsyncGenerator[ConversationResult, None]:
        """Process a sentence."""
        
        if self.agent.entry.options.get("stream"):
            return self.async_process_stream(user_input)

        response_dict = await self.agent.async_process(
            user_input.text, user_input.conversation_id
        )
        response = IntentResponse(language=user_input.language)
        response.async_set_speech(response_dict["response"])
        return ConversationResult(response=response, conversation_id=user_input.conversation_id)


    async def async_process_stream(
        self, user_input: ConversationInput
    ) -> AsyncGenerator[ConversationResult, None]:
        """Process a sentence in a stream."""
        
        yield ConversationResult(
            response=IntentResponse(language=user_input.language),
            conversation_id=user_input.conversation_id,
            event=ConversationResult.ListenEvent.INTENT_START,
        )

        try:
            async for chunk in self.agent.async_process_stream(
                user_input.text, user_input.conversation_id
            ):
                response = IntentResponse(language=user_input.language)
                response.async_set_speech(chunk)
                yield ConversationResult(
                    response=response,
                    conversation_id=user_input.conversation_id,
                    event=ConversationResult.ListenEvent.INTENT_PARTIAL_RESPONSE,
                )
        except Exception:
            _LOGGER.exception("Error during stream processing")
            response = IntentResponse(language=user_input.language)
            response.async_set_error("unknown_error", "An error occurred during streaming.")
            yield ConversationResult(response=response, conversation_id=user_input.conversation_id)
            return

        yield ConversationResult(
            response=IntentResponse(language=user_input.language),
            conversation_id=user_input.conversation_id,
            event=ConversationResult.ListenEvent.INTENT_END,
        )

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
        """Return a list of supported languages."""
        return "*"

    @property
    def has_stream_support(self) -> bool:
        """Return whether the agent supports streaming responses."""
        return self._entry.options.get("stream", False)

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Process a sentence, either by streaming or as a single response."""
        if self._agent is None:
            self._agent = LemonadeAgent(self.hass, self._entry)

        # --- ¡ESTE BLOQUE ESTÁ CORREGIDO! ---
        if self.has_stream_support:
            # 1. Creamos una respuesta de intención vacía.
            response = IntentResponse(language=user_input.language)
            # 2. Le adjuntamos nuestro generador asíncrono usando el método correcto.
            response.async_set_speech_stream(
                self._agent.async_process_stream(
                    user_input.text, user_input.conversation_id
                )
            )
            # 3. Devolvemos el resultado con esta respuesta preparada.
            return ConversationResult(
                response=response,
                conversation_id=user_input.conversation_id,
            )
        # --- FIN DEL BLOQUE CORREGIDO ---

        # El bloque 'else' (sin streaming) no cambia y ya funcionaba.
        try:
            agent_response = await self._agent.async_process(
                user_input.text, user_input.conversation_id
            )
            response = IntentResponse(language=user_input.language)
            response.async_set_speech(agent_response["response"])
            
            return ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )
        except Exception:
            _LOGGER.exception("Error processing Lemonade conversation (non-streamed)")
            
            response = IntentResponse(language=user_input.language)
            response.async_set_error(
                "intent_error",
                "Ocurrió un error inesperado al procesar la solicitud.",
            )
            return ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

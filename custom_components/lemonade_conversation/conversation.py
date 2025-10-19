# custom_components/lemonade_conversation_ha/conversation.py

import logging
from typing import Literal

from homeassistant.components.conversation import (
    ConversationAgent,
    ConversationEntity,
    ConversationResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

# Importamos la lógica que ya tenías creada
from .conversation_agent import LemonadeAgent

_LOGGER = logging.getLogger(__name__)

# Esta función es llamada por HA cuando configura la plataforma
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up conversation entities."""
    # Creamos una instancia de nuestra entidad de conversación y la añadimos a HA
    async_add_entities([LemonadeConversationEntity(hass, config_entry)])


class LemonadeConversationEntity(ConversationEntity):
    """Lemonade Conversation Agent Entity."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self._entry = entry
        # Creamos una instancia de nuestro agente lógico, pasándole la configuración
        self._agent = LemonadeAgent(hass, entry)
        # Asignamos un ID único a la entidad basado en el ID de la entrada de configuración
        self._attr_unique_id = entry.entry_id
        # El nombre que aparecerá en la interfaz de usuario de HA
        self._attr_name = "Lemonade Assistant"

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        # Soporta todos los idiomas, ya que el modelo subyacente lo hace.
        return "*"

    async def async_process(
        self, user_input: str, conversation_id: str | None = None
    ) -> ConversationResult:
        """Process a sentence."""
        _LOGGER.debug("Processing in Lemonade: %s", user_input)

        try:
            # Llamamos al método de procesamiento de nuestra clase LemonadeAgent
            agent_response = await self._agent.async_process(user_input, conversation_id)
            
            # Creamos una respuesta de intención simple.
            # Home Assistant se encargará de convertir el texto a voz.
            response = self.hass.helpers.intent.IntentResponse(self.hass)
            response.async_set_speech(agent_response["response"])

            return ConversationResult(
                response=response, conversation_id=conversation_id
            )

        except Exception as e:
            _LOGGER.error("Error processing conversation: %s", e)
            response = self.hass.helpers.intent.IntentResponse(self.hass)
            response.async_set_error(
                "intent_error",
                f"Lo siento, he tenido un problema al procesar tu solicitud: {e}",
            )
            return ConversationResult(
                response=response, conversation_id=conversation_id
            )

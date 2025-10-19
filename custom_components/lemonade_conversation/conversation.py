# custom_components/lemonade_conversation/conversation.py
import logging
from typing import Any, Dict, Optional
from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.helpers.typing import ConfigType
import openai

from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_API_KEY,
    CONF_MODEL,
    CONF_TEMPERATURE,
    CONF_MAX_TOKENS,
    CONF_VERIFY_SSL,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Any,
) -> bool:
    """Set up conversation from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data.copy()
    
    # Register the conversation agent
    async_add_entities([LemonadeConversationEntity(entry)])
    return True

class LemonadeConversationEntity(conversation.ConversationEntity):
    """Lemonade Conversation Agent."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the conversation agent."""
        self.config_entry = config_entry
        self.client = None
        self._setup_client()

    def _setup_client(self) -> None:
        """Set up the OpenAI client with Lemonade Server configuration."""
        base_url = self.config_entry.data.get(CONF_BASE_URL)
        api_key = self.config_entry.data.get(CONF_API_KEY)
        verify_ssl = self.config_entry.data.get(CONF_VERIFY_SSL, True)
        
        # Create client with Lemonade Server API
        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key or "none",
            http_client=openai.AsyncOpenAI(
                base_url=base_url,
                api_key=api_key or "none",
                http_client=openai.AsyncOpenAI(
                    base_url=base_url,
                    api_key=api_key or "none",
                    http_client=openai.AsyncOpenAI(
                        base_url=base_url,
                        api_key=api_key or "none",
                        timeout=30.0
                    )
                )
            ),
            timeout=30.0
        )

    @property
    def name(self) -> str:
        """Return the name of the agent."""
        return "Lemonade Assistant"

    @property
    def should_poll(self) -> bool:
        """Return False because the agent doesn't need polling."""
        return False

    async def async_process(self, user_input: conversation.ConversationInput) -> Any:
        """Process a conversation turn."""
        try:
            if self.client is None:
                _LOGGER.error("Lemonade client not initialized")
                return conversation.ConversationResult(
                    response="Error: Lemonade client not configured properly",
                    conversation_id=None
                )

            # Prepare the conversation history
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful home assistant. Respond to user requests in a concise way. Only respond with the information needed to fulfill the request. If you don't know how to help with a request, say so."
                }
            ]
            
            # Add conversation history if available
            if user_input.conversation_id:
                # Here we would implement the history management
                pass

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_input.text
            })

            # Call the Lemonade Server API
            response = await self.client.chat.completions.create(
                model=self.config_entry.data.get(CONF_MODEL, DEFAULT_MODEL),
                messages=messages,
                temperature=self.config_entry.data.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
                max_tokens=self.config_entry.data.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS),
                stream=False
            )

            # Extract the response
            assistant_response = response.choices[0].message.content

            return conversation.ConversationResult(
                response=assistant_response,
                conversation_id=None
            )

        except openai.APIConnectionError as ex:
            _LOGGER.error("Connection error to Lemonade Server: %s", ex)
            return conversation.ConversationResult(
                response="Sorry, I'm having trouble connecting to the AI service. Please check if Lemonade Server is running.",
                conversation_id=None
            )
        except openai.APIStatusError as ex:
            _LOGGER.error("API error from Lemonade Server: %s", ex)
            return conversation.ConversationResult(
                response="Sorry, I'm having trouble with the AI service. Please check the server logs.",
                conversation_id=None
            )
        except Exception as ex:
            _LOGGER.error("Error processing conversation: %s", ex)
            return conversation.ConversationResult(
                response="Sorry, I encountered an error processing your request.",
                conversation_id=None
            )

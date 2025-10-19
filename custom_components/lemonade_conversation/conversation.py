import logging
from typing import Any, Dict, Optional
import aiohttp

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_BASE_URL, CONF_API_KEY, CONF_MODEL, CONF_TEMPERATURE, CONF_MAX_TOKENS, CONF_VERIFY_SSL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lemonade Conversation from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data.copy()
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

class LemonadeConversationImpl:
    """Lemonade Conversation agent."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.base_url = entry.data.get(CONF_BASE_URL, "")
        self.api_key = entry.data.get(CONF_API_KEY, "")
        self.model = entry.data.get(CONF_MODEL, "Qwen3-Coder-30B-A3B-Instruct-GGUF")
        self.temperature = entry.data.get(CONF_TEMPERATURE, 0.5)
        self.max_tokens = entry.data.get(CONF_MAX_TOKENS, 150)
        self.verify_ssl = entry.data.get(CONF_VERIFY_SSL, True)
        
    @property
    def name(self) -> str:
        """Return the name of the agent."""
        return "Lemonade Conversation"

    async def async_process(self, user_input: conversation.ConversationInput) -> conversation.ConversationResult:
        """Process a sentence."""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Prepare messages for the conversation
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can control Home Assistant devices. When you receive a request, respond in a way that helps the user control their smart home."
                }
            ]
            
            # Add conversation history if available
            if hasattr(self, 'conversation_id'):
                # This would handle conversation history
                pass
            
            messages.append({
                "role": "user",
                "content": user_input.text
            })
            
            # Call Lemonade API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        _LOGGER.error(f"API error: {response.status}")
                        return conversation.ConversationResult(
                            response="Sorry, I encountered an error processing your request.",
                            conversation_id=user_input.conversation_id
                        )
                    
                    data = await response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        response_text = data['choices'][0]['message']['content'].strip()
                        return conversation.ConversationResult(
                            response=response_text,
                            conversation_id=user_input.conversation_id
                        )
                    else:
                        return conversation.ConversationResult(
                            response="Sorry, I couldn't generate a response.",
                            conversation_id=user_input.conversation_id
                        )
                        
        except Exception as ex:
            _LOGGER.error(f"Error processing conversation: {ex}")
            return conversation.ConversationResult(
                response="Sorry, I encountered an error processing your request.",
                conversation_id=user_input.conversation_id
            )

# Esta función es requerida por Home Assistant para crear el agente de conversación
async def async_get_agent(hass: HomeAssistant, entry: ConfigEntry) -> LemonadeConversationImpl:
    """Get the Lemonade Conversation agent."""
    return LemonadeConversationImpl(hass, entry)

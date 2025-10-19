# /config/custom_components/lemonade_conversation/conversation_agent.py

import logging
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

class LemonadeAgent:
    """Lemonade Conversation Agent that talks to a Lemonade Server."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.session = async_get_clientsession(hass)

    async def async_process(self, user_input: str, conversation_id: str | None = None) -> dict:
        """Process a sentence by calling the Lemonade Server."""
        
        base_url = self.entry.data.get("base_url")
        api_key = self.entry.data.get("api_key")
        model = self.entry.options.get("model", "local-model")
        
        # El endpoint es compatible con OpenAI
        url = f"{base_url.rstrip('/')}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # Por ahora, no gestionamos el historial. Cada pregunta es nueva.
        # Podríamos añadirlo en el futuro.
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": user_input}
            ]
        }
        
        _LOGGER.debug(f"Sending payload to Lemonade Server: {payload}")

        try:
            async with self.session.post(url, headers=headers, json=payload, timeout=30) as response:
                response.raise_for_status()  # Lanza un error si la respuesta no es 2xx
                data = await response.json()
                
                _LOGGER.debug(f"Received response from Lemonade Server: {data}")
                
                # Extraemos la respuesta del formato compatible con OpenAI
                message = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not message:
                    _LOGGER.error("Response from Lemonade Server is empty or malformed.")
                    return {"response": "Recibí una respuesta vacía del servidor."}
                
                return {"response": message.strip()}

        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error connecting to Lemonade Server: {err}")
            return {"response": f"No pude conectar con el servidor Lemonade: {err}"}
        except Exception as err:
            _LOGGER.error(f"An unexpected error occurred: {err}")
            return {"response": f"Ocurrió un error inesperado: {err}"}

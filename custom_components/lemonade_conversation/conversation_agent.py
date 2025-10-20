# /config/custom_components/lemonade_conversation/conversation_agent.py

import logging
import aiohttp
from collections import deque

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

# Límite de turnos de conversación (1 turno = 1 de usuario + 1 de asistente)
# Un valor de 3 significa que recordará los últimos 3 intercambios.
CONVERSATION_HISTORY_LIMIT = 3 * 2 # 6 mensajes en total

class LemonadeAgent:
    """Lemonade Conversation Agent with conversation history."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.session = async_get_clientsession(hass)
        self.history: dict[str, deque] = {} # Usamos un deque para limitar el tamaño fácilmente

    @property
    def model_in_use(self) -> str:
        """Return the model currently in use."""
        return self.entry.options.get("model", self.entry.data.get("model"))

    async def async_process(self, user_input: str, conversation_id: str | None = None) -> dict:
        """Process a sentence by calling the Lemonade Server with history."""
        
        # Obtenemos el historial para este ID de conversación. Si no existe, se crea un deque vacío.
        if conversation_id not in self.history:
            self.history[conversation_id] = deque(maxlen=CONVERSATION_HISTORY_LIMIT)
        
        current_history = self.history[conversation_id]

        # Añadimos el nuevo mensaje del usuario al historial
        current_history.append({"role": "user", "content": user_input})
        
        base_url = self.entry.data.get("base_url")
        api_key = self.entry.data.get("api_key")
        
        url = f"{base_url.rstrip('/')}/api/v1/chat/completions"
        
        headers = { "Content-Type": "application/json" }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # El payload ahora contiene todo el historial de la conversación
        payload = {
            "model": self.model_in_use,
            "messages": list(current_history) # Enviamos una lista, no el deque
        }
        
        _LOGGER.debug(f"Sending payload to Lemonade Server: URL={url}, Payload={payload}")

        try:
            async with self.session.post(url, headers=headers, json=payload, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                
                _LOGGER.debug(f"Received RAW response from Lemonade Server: {data}")
                
                try:
                    message = data["choices"][0]["message"]["content"]
                except (KeyError, IndexError, TypeError) as e:
                    _LOGGER.error(f"Failed to parse Lemonade Server response: {e}. Raw response: {data}")
                    return {"response": "Recibí una respuesta del servidor pero no pude entender su formato."}
                
                # Añadimos la respuesta del asistente al historial para el próximo turno
                assistant_response = message.strip()
                current_history.append({"role": "assistant", "content": assistant_response})
                
                return {"response": assistant_response}

        except aiohttp.ClientError as err:
            _LOGGER.error(f"Error connecting to Lemonade Server at {url}: {err}")
            return {"response": f"No pude conectar con el servidor Lemonade: {err}"}
        except Exception:
            _LOGGER.exception("An unexpected error occurred during Lemonade conversation")
            return {"response": "Ocurrió un error inesperado. Revisa los logs de Home Assistant."}

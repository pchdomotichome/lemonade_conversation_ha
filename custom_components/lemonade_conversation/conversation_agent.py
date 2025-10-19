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
        # El modelo se coge de los datos principales durante la configuración inicial
        self.model = entry.data.get("model")

    @property
    def model_in_use(self) -> str:
        """Return the model currently in use, from options or initial config."""
        # Las opciones (si se reconfiguran) tienen prioridad sobre los datos iniciales
        return self.entry.options.get("model", self.model)

    async def async_process(self, user_input: str, conversation_id: str | None = None) -> dict:
        """Process a sentence by calling the Lemonade Server."""
        
        base_url = self.entry.data.get("base_url")
        api_key = self.entry.data.get("api_key")
        
        # ¡CORRECCIÓN CLAVE DE LA URL!
        url = f"{base_url.rstrip('/')}/api/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
        }
        # Solo añadimos el encabezado de autorización si se proporcionó una API Key
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        payload = {
            "model": self.model_in_use,
            "messages": [
                {"role": "user", "content": user_input}
            ]
        }
        
        _LOGGER.debug(f"Sending payload to Lemonade Server: URL={url}, Payload={payload}")

        try:
            async with self.session.post(url, headers=headers, json=payload, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                
                _LOGGER.debug(f"Received response from Lemonade Server: {data}")
                
                message = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not message:
                    _LOGGER.error("Response from Lemonade Server is empty or malformed.")
                    return {"response": "Recibí una respuesta vacía del servidor."}
                
                return {"response": message.strip()}

        except aiohttp.ClientError as err:
            # Este log es el que nos daría la pista del error 404
            _LOGGER.error(f"Error connecting to Lemonade Server at {url}: {err}")
            return {"response": f"No pude conectar con el servidor Lemonade: {err}"}
        except Exception as err:
            _LOGGER.exception("An unexpected error occurred during Lemonade conversation")
            return {"response": f"Ocurrió un error inesperado. Revisa los logs de Home Assistant para más detalles."}

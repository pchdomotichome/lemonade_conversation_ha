# /config/custom_components/lemonade_conversation/conversation_agent.py

import logging
import aiohttp
import json
from collections import deque
from typing import AsyncGenerator

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

CONVERSATION_HISTORY_LIMIT = 6 # 3 turnos (user + assistant)

class LemonadeAgent:
    """Lemonade Conversation Agent with conversation history and streaming."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.session = async_get_clientsession(hass)
        self.history: dict[str, deque] = {}

    @property
    def model_in_use(self) -> str:
        """Return the model currently in use."""
        return self.entry.options.get("model", self.entry.data.get("model"))

    def _prepare_payload(self, user_input: str, conversation_id: str | None, stream: bool) -> tuple[dict, deque]:
        """Prepare the payload and update history."""
        opts = self.entry.options
        system_prompt = opts.get("system_prompt", "")
        temperature = opts.get("temperature")
        top_k = opts.get("top_k")
        top_p = opts.get("top_p")
        
        if conversation_id not in self.history:
            self.history[conversation_id] = deque(maxlen=CONVERSATION_HISTORY_LIMIT)
        
        current_history = self.history[conversation_id]
        
        if not current_history and system_prompt:
            current_history.append({"role": "system", "content": system_prompt})

        current_history.append({"role": "user", "content": user_input})
        
        payload = {
            "model": self.model_in_use,
            "messages": list(current_history),
            "stream": stream
        }
        
        if temperature is not None: payload["temperature"] = temperature
        if top_k is not None: payload["top_k"] = top_k
        if top_p is not None: payload["top_p"] = top_p
        
        return payload, current_history

    async def async_process(self, user_input: str, conversation_id: str | None = None) -> dict:
        """Process a sentence as a single response."""
        payload, current_history = self._prepare_payload(user_input, conversation_id, stream=False)
        
        base_url = self.entry.data.get("base_url")
        api_key = self.entry.data.get("api_key")
        url = f"{base_url.rstrip('/')}/api/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if api_key: headers["Authorization"] = f"Bearer {api_key}"
        
        _LOGGER.debug(f"Sending payload (non-stream): {payload}")

        try:
            async with self.session.post(url, headers=headers, json=payload, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug(f"Received RAW response: {data}")
                
                try:
                    message = data["choices"][0]["message"]["content"]
                except (KeyError, IndexError, TypeError) as e:
                    _LOGGER.error(f"Failed to parse response: {e}. Raw: {data}")
                    return {"response": "Could not parse server response."}
                
                assistant_response = message.strip()
                current_history.append({"role": "assistant", "content": assistant_response})
                return {"response": assistant_response}

        except aiohttp.ClientError as err:
            _LOGGER.error(f"Connection error: {err}")
            return {"response": "Could not connect to the server."}
        except Exception:
            _LOGGER.exception("Unexpected error during non-stream processing")
            return {"response": "An unexpected error occurred."}

    async def async_process_stream(self, user_input: str, conversation_id: str | None = None) -> AsyncGenerator[str, None]:
        """Process a sentence by streaming the response."""
        payload, current_history = self._prepare_payload(user_input, conversation_id, stream=True)

        base_url = self.entry.data.get("base_url")
        api_key = self.entry.data.get("api_key")
        url = f"{base_url.rstrip('/')}/api/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if api_key: headers["Authorization"] = f"Bearer {api_key}"
        
        _LOGGER.debug(f"Streaming payload: {payload}")
        
        full_response = ""
        try:
            async with self.session.post(url, headers=headers, json=payload, timeout=300) as response:
                response.raise_for_status()
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data:'):
                        data_str = line[5:].strip()
                        if data_str == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data_str)
                            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                            if content:
                                full_response += content
                                yield content
                        except json.JSONDecodeError:
                            continue
        except Exception:
            _LOGGER.exception("Error during stream processing")
            yield "An error occurred during streaming."
        
        current_history.append({"role": "assistant", "content": full_response})

# /config/custom_components/lemonade_conversation/conversation_agent.py

import logging
import aiohttp
import json # Necesitamos el módulo json
from collections import deque
from typing import AsyncGenerator # Importamos AsyncGenerator

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

# ... (constantes y la clase LemonadeAgent hasta async_process)

class LemonadeAgent:
    # ... (__init__ y properties no cambian) ...

    # --- MÉTODO PARA RESPUESTAS COMPLETAS (SIN STREAM) ---
    async def async_process(self, user_input: str, conversation_id: str | None = None) -> dict:
        # (La lógica que ya teníamos, pero asegurándonos de que stream=False)
        opts = self.entry.options
        system_prompt = opts.get("system_prompt", "")
        # ... (obtener temperature, top_k, top_p) ...
        # ... (gestión del historial) ...
        # ... (construcción de headers) ...
        
        payload = {
            "model": self.model_in_use,
            "messages": list(current_history),
            "stream": False # Aseguramos que no se haga stream
        }
        # ... (añadir temperature, etc. al payload) ...
        
        try:
            # ... (código existente para la llamada y parseo) ...
        except Exception:
            # ... (manejo de errores) ...

    # --- NUEVO MÉTODO PARA RESPUESTAS EN STREAM ---
    async def async_process_stream(self, user_input: str, conversation_id: str | None = None) -> AsyncGenerator[str, None]:
        """Process a sentence by streaming the response from the Lemonade Server."""
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

        base_url = self.entry.data.get("base_url")
        api_key = self.entry.data.get("api_key")
        url = f"{base_url.rstrip('/')}/api/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if api_key: headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": self.model_in_use,
            "messages": list(current_history),
            "stream": True # ¡La clave está aquí!
        }
        if temperature is not None: payload["temperature"] = temperature
        if top_k is not None: payload["top_k"] = top_k
        if top_p is not None: payload["top_p"] = top_p
        
        _LOGGER.debug(f"Streaming payload to Lemonade Server: {payload}")
        
        full_response = ""
        try:
            async with self.session.post(url, headers=headers, json=payload, timeout=300) as response:
                response.raise_for_status()
                # Leemos la respuesta línea por línea
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data:'):
                        # Quitamos el prefijo "data: "
                        data_str = line[5:].strip()
                        if data_str == '[DONE]':
                            break
                        try:
                            # Parseamos el JSON de cada evento
                            chunk = json.loads(data_str)
                            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                            if content:
                                full_response += content
                                yield content # Devolvemos cada trozo de texto
                        except json.JSONDecodeError:
                            _LOGGER.warning(f"Could not decode stream chunk: {data_str}")
                            continue

        except Exception:
            _LOGGER.exception("Error during Lemonade stream processing")
            yield "Ocurrió un error durante el procesamiento del stream."
        
        # Al final, guardamos la respuesta completa en el historial
        current_history.append({"role": "assistant", "content": full_response})

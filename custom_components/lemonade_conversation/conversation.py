"""Conversation agent for Lemonade integration."""
from __future__ import annotations

import json
import logging
from typing import Any, Literal

from homeassistant.components.conversation import (
    ConversationEntity,
    ConversationInput,
    ConversationResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_FRIENDLY_NAME, MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import ulid

from .const import (
    CONF_MAX_TOKENS,
    CONF_MODEL,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_K,
    CONF_TOP_P,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
    DOMAIN,
    MAX_HISTORY_MESSAGES,
)
from .exceptions import (
    LemonadeConnectionError,
    LemonadeException,
    LemonadeTimeoutError,
)
from .helpers import LemonadeClient, truncate_message_history

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up conversation entities."""
    agent = LemonadeConversationEntity(hass, config_entry)
    async_add_entities([agent])


class LemonadeConversationEntity(ConversationEntity):
    """Lemonade conversation agent."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = config_entry
        self._attr_unique_id = config_entry.entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Lemonade Conversation",
            "manufacturer": "Lemonade",
            "model": "Conversation Agent",
        }
        self.history: dict[str, list[dict[str, str]]] = {}

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return supported languages."""
        return MATCH_ALL

    def _get_states_context(self) -> str:
        """Get a string with the state of relevant entities."""
        states_context = "\n\n### ESTADO ACTUAL DEL HOGAR ###\n"
        light_states = []
        for state in self.hass.states.async_all("light"):
            friendly_name = state.attributes.get(ATTR_FRIENDLY_NAME, state.entity_id)
            light_states.append(f"- {state.entity_id} ({friendly_name}): {state.state}")

        if light_states:
            states_context += "Luces:\n"
            states_context += "\n".join(light_states)
        
        states_context += "\n#################################\n"
        return states_context

    def _get_manual_tools(self) -> list[dict[str, Any]]:
        """Return manual tools for basic home control operations."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "HassTurnOn",
                    "description": "Turn on a light or switch",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string", 
                                "description": "Entity ID or friendly name"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "HassTurnOff",
                    "description": "Turn off a light or switch",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "name": {
                                "type": "string", 
                                "description": "Entity ID or friendly name"
                            }
                        },
                        "required": ["name"]
                    }
                }
            }
        ]

    async def async_process(
        self, user_input: ConversationInput
    ) -> ConversationResult:
        """Process a sentence."""
        options = self.entry.options

        # Read configuration
        model = str(options.get(CONF_MODEL, DEFAULT_MODEL))
        temperature = float(options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE))
        top_p = float(options.get(CONF_TOP_P, DEFAULT_TOP_P))
        top_k = int(options.get(CONF_TOP_K, DEFAULT_TOP_K))
        max_tokens = int(options.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS))
        prompt = options.get(CONF_PROMPT, DEFAULT_PROMPT)

        # Get or create conversation history
        conversation_id = user_input.conversation_id or ulid.ulid_now()
        if conversation_id not in self.history:
            self.history[conversation_id] = []
            if prompt:
                self.history[conversation_id].append(
                    {"role": "system", "content": prompt}
                )

        # Inject states context into system message
        system_message_content = f"{prompt}\n{self._get_states_context()}"
        if self.history[conversation_id] and self.history[conversation_id][0]["role"] == "system":
            self.history[conversation_id][0]["content"] = system_message_content
        else:
            self.history[conversation_id].insert(0, {"role": "system", "content": system_message_content})

        # Add user message (clean, without context injection)
        self.history[conversation_id].append({"role": "user", "content": user_input.text})

        # Truncate history if needed
        self.history[conversation_id] = truncate_message_history(
            self.history[conversation_id], MAX_HISTORY_MESSAGES
        )

        try:
            # Get tools and client
            tools = self._get_manual_tools()
            client: LemonadeClient = self.hass.data[DOMAIN][self.entry.entry_id]

            # First API call
            response_data = await client.async_chat_completion(
                messages=self.history[conversation_id],
                model=model,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_tokens=max_tokens,
                tools=tools,
            )

            if not response_data.get("choices"):
                raise LemonadeException("No choices in response")

            choice = response_data["choices"][0]
            message = choice.get("message", {})

            # Handle tool calls
            if tool_calls := message.get("tool_calls"):
                self.history[conversation_id].append(message)
                tool_results = await self._async_execute_tools(tool_calls)
                
                for tool_result in tool_results:
                    self.history[conversation_id].append(tool_result)

                # Second API call with tool results
                response_data = await client.async_chat_completion(
                    messages=self.history[conversation_id],
                    model=model,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    max_tokens=max_tokens,
                    tools=tools,
                )
                
                choice = response_data["choices"][0]
                message = choice.get("message", {})

            # Get final response
            response_text = (message.get("content") or "").strip()
            if not response_text:
                response_text = "Lo siento, no pude generar una respuesta."

            # Add to history
            self.history[conversation_id].append(
                {"role": "assistant", "content": response_text}
            )

        except LemonadeTimeoutError:
            _LOGGER.error("Timeout communicating with Lemonade server")
            response_text = "Lo siento, la conexión tardó demasiado."
        except LemonadeConnectionError:
            _LOGGER.error("Failed to connect to Lemonade server")
            response_text = "Lo siento, no puedo conectarme al servidor Lemonade."
        except LemonadeException as err:
            _LOGGER.error("Lemonade API error: %s", err)
            response_text = "Lo siento, hubo un error procesando tu solicitud."
        except Exception as err:
            _LOGGER.exception("Unexpected error processing conversation: %s", err)
            response_text = "Lo siento, ocurrió un error inesperado."

        # Create response - exactly as Google does
        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(response_text)  # Without language parameter

        return ConversationResult(
            response=intent_response,
            conversation_id=conversation_id,
        )

    async def _async_execute_tools(
        self, tool_calls: list[dict[str, Any]]
    ) -> list[dict[str, str]]:
        """Execute tool calls using direct service calls."""
        tool_results: list[dict[str, str]] = []

        for tool_call in tool_calls:
            tool_id, function_name, arguments = self._parse_tool_call(tool_call)
            if function_name is None:
                continue

            _LOGGER.debug("Executing tool: %s with arguments: %s", function_name, arguments)

            try:
                result = await self._async_execute_direct_service(function_name, arguments)
                tool_results.append({
                    "role": "tool", 
                    "tool_call_id": tool_id, 
                    "content": json.dumps(result or {"success": True})
                })
            except Exception as err:
                _LOGGER.error("Error executing tool %s: %s", function_name, err)
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": json.dumps({"error": str(err)}),
                })

        return tool_results

    async def _async_execute_direct_service(self, function_name: str, arguments: dict):
        """Execute service calls directly for tool operations."""
        entity_id = arguments.get("name")
        if not entity_id:
            raise Exception("Missing entity name")

        if function_name == "HassTurnOn":
            await self.hass.services.async_call("light", "turn_on", {"entity_id": entity_id})
            return {"status": "turned_on", "entity": entity_id}
            
        elif function_name == "HassTurnOff":
            await self.hass.services.async_call("light", "turn_off", {"entity_id": entity_id})
            return {"status": "turned_off", "entity": entity_id}
            
        else:
            raise Exception(f"Unsupported tool: {function_name}")

    def _parse_tool_call(self, tool_call: dict[str, Any]) -> tuple[str, str | None, dict[str, Any]]:
        """Parse tool call and return (tool_id, function_name, arguments)."""
        tool_id = tool_call.get("id", "")
        function = tool_call.get("function", {})
        function_name = function.get("name")
        try:
            arguments_str = function.get("arguments", "{}")
            arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
        except json.JSONDecodeError:
            _LOGGER.error("Failed to parse tool arguments: %s", arguments_str)
            return tool_id, None, {}
        return tool_id, function_name, arguments

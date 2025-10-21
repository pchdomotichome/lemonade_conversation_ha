"""Helper functions for Lemonade Conversation integration."""
import asyncio
import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    ENDPOINT_CHAT,
    ENDPOINT_MODELS,
    DEFAULT_TIMEOUT,
)
from .exceptions import (
    LemonadeAPIError,
    LemonadeConnectionError,
    LemonadeInvalidResponseError,
    LemonadeTimeoutError,
)

_LOGGER = logging.getLogger(__name__)


class LemonadeClient:
    """Client for interacting with Lemonade Server."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Lemonade client."""
        self.hass = hass
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = async_get_clientsession(hass)

    async def async_test_connection(self) -> bool:
        """Test connection to Lemonade server."""
        try:
            await self.async_get_models()
            return True
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False

    async def async_get_models(self) -> list[dict[str, Any]]:
        """Get available models from Lemonade server."""
        url = f"{self.base_url}{ENDPOINT_MODELS}"

        try:
            async with asyncio.timeout(self.timeout):
                async with self._session.get(url) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise LemonadeAPIError(
                            f"Failed to get models: {response.status} - {text}"
                        )

                    data = await response.json()

                    if not isinstance(data, dict) or "data" not in data:
                        raise LemonadeInvalidResponseError(
                            "Invalid response format from models endpoint"
                        )

                    return data["data"]

        except asyncio.TimeoutError as err:
            raise LemonadeTimeoutError(
                f"Timeout connecting to Lemonade server at {url}"
            ) from err
        except aiohttp.ClientError as err:
            raise LemonadeConnectionError(
                f"Failed to connect to Lemonade server at {url}: {err}"
            ) from err
        except Exception as err:
            raise LemonadeAPIError(f"Unexpected error: {err}") from err

    async def async_chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
        top_p: float,
        top_k: int,
        max_tokens: int,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send chat completion request to Lemonade server."""
        url = f"{self.base_url}{ENDPOINT_CHAT}"

        payload: dict[str, Any] = {
            "model": str(model),
            "messages": messages,
            "temperature": float(temperature),
            "top_p": float(top_p),
            "top_k": int(top_k),
            "max_tokens": int(max_tokens),
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        _LOGGER.debug("Sending chat completion request")

        try:
            async with asyncio.timeout(self.timeout):
                async with self._session.post(url, json=payload) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise LemonadeAPIError(
                            f"Chat completion failed: {response.status} - {text}"
                        )

                    data = await response.json()
                    _LOGGER.debug("Received response from Lemonade")

                    if not isinstance(data, dict) or "choices" not in data:
                        raise LemonadeInvalidResponseError(
                            "Invalid response format from chat endpoint"
                        )

                    return data

        except asyncio.TimeoutError as err:
            raise LemonadeTimeoutError("Timeout during chat completion request") from err
        except aiohttp.ClientError as err:
            raise LemonadeConnectionError(f"Connection error: {err}") from err
        except Exception as err:
            raise LemonadeAPIError(f"Unexpected error: {err}") from err


def truncate_message_history(
    messages: list[dict[str, str]],
    max_messages: int,
) -> list[dict[str, str]]:
    """Truncate message history keeping system message and recent messages."""
    if len(messages) <= max_messages:
        return messages

    # Always keep system message if present
    if messages and messages[0].get("role") == "system":
        return [messages[0]] + messages[-(max_messages - 1) :]

    return messages[-max_messages:]

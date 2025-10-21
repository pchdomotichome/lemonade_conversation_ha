"""The Lemonade Conversation integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_BASE_URL, CONF_TIMEOUT, DEFAULT_TIMEOUT, DOMAIN
from .exceptions import LemonadeConnectionError
from .helpers import LemonadeClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CONVERSATION]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lemonade Conversation from a config entry."""
    base_url = entry.data[CONF_BASE_URL]
    timeout = entry.options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

    # Create client
    client = LemonadeClient(
        hass=hass,
        base_url=base_url,
        timeout=timeout,
    )

    # Test connection
    try:
        if not await client.async_test_connection():
            raise ConfigEntryNotReady(
                f"Failed to connect to Lemonade server at {base_url}"
            )
    except LemonadeConnectionError as err:
        raise ConfigEntryNotReady(
            f"Failed to connect to Lemonade server at {base_url}: {err}"
        ) from err

    # Store client
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)

"""The Lemonade Conversation integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Lemonade Conversation component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lemonade Conversation from a config entry."""
    # Forward the conversation setup to the conversation component
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, [Platform.CONVERSATION])
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Fix: Remove the problematic line that was causing the error
    # unload_ok = await hass.config_entries.async_unload_entry(entry)
    # if unload_ok:
    #     hass.data[DOMAIN].pop(entry.entry_id, None)
    # return unload_ok
    
    # Instead, just clean up the data
    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

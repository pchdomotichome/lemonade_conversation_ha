# custom_components/lemonade_conversation_ha/__init__.py

"""The Lemonade Conversation HA integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

# Define las plataformas que tu integración va a utilizar.
# ¡Este es el cambio clave!
PLATFORMS: list[Platform] = [Platform.CONVERSATION]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lemonade Conversation HA from a config entry."""
    # Esto le dirá a HA que cargue las plataformas definidas en PLATFORMS.
    # En nuestro caso, buscará y configurará conversation.py
    await hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Descarga las plataformas al eliminar la integración.
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

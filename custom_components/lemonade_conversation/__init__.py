# /config/custom_components/lemonade_conversation/__init__.py

"""The Lemonade Conversation HA integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

# Ahora sí, declaramos la plataforma que vamos a usar.
PLATFORMS: list[Platform] = [Platform.CONVERSATION]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lemonade Conversation HA from a config entry."""
    # Reenvía la configuración a la plataforma 'conversation'.
    # HA buscará 'conversation.py' y ejecutará su 'async_setup_entry'.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Descarga la plataforma correctamente.
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

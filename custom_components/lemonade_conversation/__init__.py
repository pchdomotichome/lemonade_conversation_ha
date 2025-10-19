# custom_components/lemonade_conversation_ha/__init__.py

"""The Lemonade Conversation HA integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

# Define las plataformas que tu integración va a utilizar.
PLATFORMS: list[Platform] = [Platform.CONVERSATION]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lemonade Conversation HA from a config entry."""
    # ESTA ES LA LÍNEA CORREGIDA
    # Reenvía la configuración de la entrada a las plataformas especificadas en PLATFORMS.
    # Home Assistant buscará conversation.py y llamará a su async_setup_entry.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Esto descargará correctamente las entidades creadas por nuestras plataformas.
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

"""Constants for the Lemonade Conversation integration."""
from typing import Final

DOMAIN: Final = "lemonade_conversation"

# Configuration
CONF_BASE_URL: Final = "base_url"
CONF_MODEL: Final = "model"
CONF_TEMPERATURE: Final = "temperature"
CONF_TOP_P: Final = "top_p"
CONF_TOP_K: Final = "top_k"
CONF_MAX_TOKENS: Final = "max_tokens"
CONF_PROMPT: Final = "prompt"
CONF_TIMEOUT: Final = "timeout"

# Defaults
DEFAULT_NAME: Final = "Lemonade Conversation"
DEFAULT_BASE_URL: Final = "http://192.168.30.61:8000"
DEFAULT_MODEL: Final = "Qwen3-Coder-30B-A3B-Instruct-GGUF"
DEFAULT_TEMPERATURE: Final = 0.7
DEFAULT_TOP_P: Final = 0.9
DEFAULT_TOP_K: Final = 40
DEFAULT_MAX_TOKENS: Final = 2048
DEFAULT_TIMEOUT: Final = 30
DEFAULT_PROMPT: Final = """Eres un asistente de hogar inteligente llamado Lemonade.
Tu objetivo es ayudar al usuario a controlar su hogar y responder sus preguntas.

Directrices importantes:
- Responde de manera concisa y útil
- Si no estás seguro, di que no lo sabes
- Prioriza la seguridad y privacidad del usuario
- Usa un tono amigable y profesional
- Cuando controles dispositivos, confirma las acciones realizadas
"""

# API Endpoints
ENDPOINT_CHAT: Final = "/api/v1/chat/completions"
ENDPOINT_MODELS: Final = "/api/v1/models"

# Limits
MIN_TEMPERATURE: Final = 0.0
MAX_TEMPERATURE: Final = 2.0
MIN_TOP_P: Final = 0.0
MAX_TOP_P: Final = 1.0
MIN_TOP_K: Final = 1
MAX_TOP_K: Final = 100
MIN_MAX_TOKENS: Final = 1
MAX_MAX_TOKENS: Final = 32768
MIN_TIMEOUT: Final = 5
MAX_TIMEOUT: Final = 120

# Conversation
MAX_HISTORY_MESSAGES: Final = 10
SUPPORTED_LANGUAGES: Final = ["es", "en", "fr", "de", "it", "pt"]

# Attributes
ATTR_MODEL: Final = "model"
ATTR_TEMPERATURE: Final = "temperature"
ATTR_TOP_P: Final = "top_p"
ATTR_TOP_K: Final = "top_k"
ATTR_MAX_TOKENS: Final = "max_tokens"

# /config/custom_components/lemonade_conversation/conversation_agent.py

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

class LemonadeAgent:
    """Lemonade Conversation Agent."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.history = {} # Un diccionario para gestionar múltiples conversaciones

    async def async_process(self, user_input: str, conversation_id: str | None = None) -> dict:
        """Process a sentence."""
        
        # --- Lazy loading de las librerías pesadas ---
        from langchain.chains import ConversationChain
        from langchain_openai import ChatOpenAI
        from langchain.memory import ConversationBufferWindowMemory
        from langchain.prompts import (
            ChatPromptTemplate,
            HumanMessagePromptTemplate,
            MessagesPlaceholder,
            SystemMessagePromptTemplate,
        )
        
        api_key = self.entry.data.get("api_key")
        model = self.entry.options.get("model", "gpt-3.5-turbo")
        
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    "The following is a friendly conversation between a human and an AI."
                ),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )

        if conversation_id not in self.history:
            self.history[conversation_id] = ConversationBufferWindowMemory(
                k=3, return_messages=True
            )
        
        memory = self.history[conversation_id]

        llm = ChatOpenAI(model_name=model, temperature=0, openai_api_key=api_key)
        
        conversation = ConversationChain(llm=llm, prompt=prompt, verbose=True, memory=memory)

        # Ejecutar la llamada a la API en el executor para no bloquear el bucle de eventos.
        result = await self.hass.async_add_executor_job(
            conversation.predict, input=user_input
        )
        
        _LOGGER.debug(f"Response: {result}")

        return {"response": result}

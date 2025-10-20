# /config/custom_components/lemonade_conversation/config_flow.py

# ... (todas las importaciones y funciones hasta LemonadeOptionsFlowHandler)
# ... (LemonadeConfigFlow no cambia)

class LemonadeOptionsFlowHandler(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Show the main menu for options."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["general", "personality", "parameters", "advanced"], # Añadimos el nuevo menú
        )

    # (async_step_general y async_step_personality no cambian)
    async def async_step_general(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        # ... código existente ...

    async def async_step_personality(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        # ... código existente ...

    async def async_step_parameters(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        # ... código existente ...

    # --- NUEVA FUNCIÓN PARA EL MENÚ ADVANCED ---
    async def async_step_advanced(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle advanced settings."""
        if user_input is not None:
            return self.async_create_entry(title="", data={**self.config_entry.options, **user_input})

        return self.async_show_form(
            step_id="advanced",
            data_schema=vol.Schema({
                vol.Optional(
                    "stream",
                    default=self.config_entry.options.get("stream", False)
                ): bool,
            })
        )

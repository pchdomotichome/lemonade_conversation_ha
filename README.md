### Work In PROGRESS. Don't Use IT ###

# 🍋 Lemonade Conversation for Home Assistant

**Integración de Lemonade Server como agente de conversación para Home Assistant**

[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/pchdomotichome/lemonade_conversation_ha)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.8+-green)](https://www.home-assistant.io)

## ✨ Características

- 🤖 **Agente de Conversación** con Lemonade Server local
- 🏠 **Control de Dispositivos** mediante comandos de voz/texto  
- 🔍 **Consulta de Estados** en tiempo real con inyección de contexto
- ⚙️ **Configuración UI** completa (Config Flow + Options Flow)
- 🌐 **Soporte Multi-idioma**
- 💬 **Chat Log** integrado con Home Assistant

## 🚀 Instalación

### Método 1: HACS (Próximamente)
1. Agrega este repositorio a HACS
2. Busca "Lemonade Conversation"
3. Instala y reinicia

### Método 2: Manual
1. Copia la carpeta `lemonade_conversation` a `custom_components`
2. Reinicia Home Assistant
3. Ve a **Configuración → Dispositivos y Servicios → Integraciones**
4. Haz clic en **Agregar Integración** y busca "Lemonade Conversation"

## ⚙️ Configuración

### Requisitos
- Home Assistant 2023.8 o superior
- Servidor Lemonade ejecutándose

### Configuración Inicial
- **URL Base**: URL de tu servidor Lemonade (ej: `http://192.168.30.61:8000`)
- **Modelo**: Modelo a utilizar (ej: `Qwen3-Coder-30B-A3B-Instruct-GGUF`)
- **Temperatura**: Control de creatividad (0.0 - 2.0)

### Opciones Avanzadas
- **Top P** - Nucleus sampling
- **Top K** - Diversidad de respuestas  
- **Max Tokens** - Límite de respuesta
- **Prompt** - Prompt del sistema personalizado
- **Timeout** - Tiempo de espera (segundos)

## 💡 Ejemplos de Uso

### Consultas de Estado
"¿Qué luces están encendidas?"
"Me podés decir el estado de las luces del bunker?"
"¿Hay alguna luz encendida en la cocina?"


## 🐛 Reportar Problemas

Si encuentras algún problema, por favor [abre un issue](https://github.com/pchdomotichome/lemonade_conversation_ha/issues).

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor, lee las guías de contribución.

## 📄 Licencia

MIT License

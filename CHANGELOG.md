# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [0.1.0] - 2024-10-20

### 🎉 Release Inicial

Primera versión funcional de Lemonade Conversation para Home Assistant.

#### ✨ Agregado

- **Integración completa** de Lemonade Server como agente de conversación
- **Config Flow** con interfaz de usuario profesional
- **Options Flow** para configuración dinámica sin reiniciar
- **Tool Calling** para control de dispositivos
- **Inyección de Contexto** automática para estados en tiempo real
- **Manejo de Historial** de conversación por sesión
- **Soporte multi-idioma** (español, inglés, francés, alemán, italiano, portugués)
- **Integración nativa** con Home Assistant Assist
- Control de luces mediante comandos naturales
- Consulta de estados de dispositivos en tiempo real

#### 🚀 Características Principales

- Consulta de estados de dispositivos
- Control de encendido/apagado de luces
- Configuración de parámetros del modelo:
  - Temperature (0.0 - 2.0)
  - Top P (0.0 - 1.0)
  - Top K (1 - 100)
  - Max Tokens (1 - 32768)
- Prompt del sistema personalizable
- Timeout configurable (5 - 120 segundos)
- Manejo robusto de errores y timeouts
- Logging detallado para debugging
- Chat log integrado con Home Assistant

#### 🔧 Técnico

- Arquitectura basada en patrones oficiales de Home Assistant
- Cliente HTTP asíncrono con aiohttp
- Manejo de excepciones específicas
- Truncado inteligente de historial de mensajes
- Compatibilidad con Home Assistant 2023.8+
- Ejecuta herramientas mediante llamadas directas a servicios
- Sistema de fallback para máxima compatibilidad

#### 📚 Documentación

- README completo con ejemplos de uso
- Configuración para HACS
- Traducciones en español e inglés
- Documentación de opciones avanzadas

---

## [Unreleased]

### Planificado para v0.2.0

- Scripts de Home Assistant como funciones
- Soporte para más dominios (switches, covers, climate)
- Aliases personalizados para entidades
- Memoria persistente entre reinicios
- Funciones REST personalizadas
- Templates avanzados con Jinja2
- Confirmaciones para acciones críticas
- Control de volumen y brillo
- Soporte para grupos de dispositivos

---

[0.1.0]: https://github.com/pchdomotichome/lemonade_conversation_ha/releases/tag/v0.1.0
[Unreleased]: https://github.com/pchdomotichome/lemonade_conversation_ha/compare/v0.1.0...HEAD

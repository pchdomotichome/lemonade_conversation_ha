# 🤝 Guía de Contribución

¡Gracias por tu interés en contribuir a Lemonade Conversation! 🍋

Todas las contribuciones son bienvenidas, ya sean reportes de bugs, nuevas características, mejoras en la documentación o traducciones.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo Contribuir?](#cómo-contribuir)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Características](#sugerir-características)
- [Configuración del Entorno](#configuración-del-entorno)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Estándares de Código](#estándares-de-código)
- [Documentación](#documentación)
- [Traducciones](#traducciones)

## 📜 Código de Conducta

Este proyecto adhiere a un código de conducta. Al participar, se espera que respetes este código. Por favor, sé respetuoso y profesional en todas las interacciones.

## 🚀 ¿Cómo Contribuir?

1. **Fork el repositorio**
2. **Crea tu rama de características** (`git checkout -b feature/AmazingFeature`)
3. **Haz tus cambios**
4. **Commit tus cambios** (`git commit -m 'Add: nueva característica increíble'`)
5. **Push a la rama** (`git push origin feature/AmazingFeature`)
6. **Abre un Pull Request**

## 🐛 Reportar Bugs

Los bugs son rastreados como [GitHub issues](https://github.com/pchdomotichome/lemonade_conversation_ha/issues).

Antes de crear un reporte de bug:
- Verifica que el bug no haya sido reportado antes
- Verifica que estés usando la última versión

Al reportar un bug, incluye:
- Descripción clara del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Logs relevantes
- Información del sistema

Usa la plantilla de [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md).

## 💡 Sugerir Características

Las sugerencias de características también se rastrean como [GitHub issues](https://github.com/pchdomotichome/lemonade_conversation_ha/issues).

Antes de sugerir una característica:
- Verifica que no haya sido sugerida antes
- Considera si es relevante para el proyecto

Al sugerir una característica, incluye:
- Descripción clara de la característica
- Motivación y casos de uso
- Posibles implementaciones
- Mockups o ejemplos si aplica

Usa la plantilla de [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md).

## 🔧 Configuración del Entorno

### Requisitos Previos

- Python 3.11+
- Home Assistant Core (para desarrollo)
- Git

### Instalación para Desarrollo

1. **Clona tu fork:**
```bash
git clone https://github.com/tu-usuario/lemonade_conversation_ha.git
cd lemonade_conversation_ha
```

2. **Crea un entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instala dependencias de desarrollo:**
```bash
pip install -r requirements-dev.txt
```

4. **Configura pre-commit hooks:**
```bash
pre-commit install
```

### Testing Local

1. **Copia la integración a tu instalación de HA:**
```bash
cp -r custom_components/lemonade_conversation /path/to/ha/config/custom_components/
```

2. **Reinicia Home Assistant**

3. **Verifica los logs:**
```bash
tail -f /path/to/ha/config/home-assistant.log
```

## 🔄 Proceso de Pull Request

1. **Actualiza tu fork:**
```bash
git remote add upstream https://github.com/pchdomotichome/lemonade_conversation_ha.git
git fetch upstream
git checkout main
git merge upstream/main
```

2. **Crea una rama descriptiva:**
```bash
git checkout -b feature/descripcion-corta
# o
git checkout -b fix/bug-especifico
```

3. **Haz cambios pequeños y atómicos**
   - Un PR = Una característica/fix
   - Commits descriptivos

4. **Prueba tus cambios:**
   - Verifica que funcione en tu HA local
   - Ejecuta linters si están disponibles
   - Asegúrate de no romper funcionalidad existente

5. **Documenta tus cambios:**
   - Actualiza README si es necesario
   - Actualiza CHANGELOG.md
   - Comenta código complejo

6. **Abre el Pull Request:**
   - Usa un título descriptivo
   - Referencia issues relacionados (#123)
   - Describe qué cambia y por qué
   - Incluye capturas si hay cambios visuales

### Plantilla de PR

```markdown
## Descripción
Breve descripción de los cambios

## Tipo de cambio
- [ ] Bug fix
- [ ] Nueva característica
- [ ] Breaking change
- [ ] Documentación

## Checklist
- [ ] Mi código sigue el estilo del proyecto
- [ ] He probado mis cambios
- [ ] He actualizado la documentación
- [ ] He agregado tests si aplica
- [ ] Todos los tests pasan

## Screenshots (si aplica)

## Issues relacionados
Fixes #(issue)
```

## 📝 Estándares de Código

### Python

- Sigue [PEP 8](https://pep8.org/)
- Usa type hints cuando sea posible
- Documenta funciones con docstrings
- Nombres descriptivos de variables

### Ejemplo:
```python
async def async_process_command(
    self, 
    command: str, 
    context: dict[str, Any]
) -> str:
    """Process a user command and return response.
    
    Args:
        command: The user's input command
        context: Additional context for processing
        
    Returns:
        The processed response string
    """
    # Implementation here
    pass
```

### Commits

Usa mensajes de commit descriptivos:
- `Add: nueva característica X`
- `Fix: corregir bug en Y`
- `Update: mejorar rendimiento de Z`
- `Docs: actualizar README`
- `Refactor: reorganizar módulo A`

## 📚 Documentación

- Mantén el README actualizado
- Documenta nuevas características
- Incluye ejemplos de uso
- Actualiza CHANGELOG.md

## 🌐 Traducciones

Para agregar un nuevo idioma:

1. Crea archivo en `translations/XX.json` (XX = código idioma)
2. Traduce todas las strings de `strings.json`
3. Prueba que funcione correctamente
4. Actualiza la lista de idiomas soportados

## ❓ Preguntas

Si tienes preguntas, puedes:
- Abrir un [Discussion](https://github.com/pchdomotichome/lemonade_conversation_ha/discussions)
- Crear un issue con la etiqueta `question`
- Contactar a los maintainers

## 🙏 Reconocimientos

¡Gracias a todos los contribuidores que hacen este proyecto mejor!

## 📄 Licencia

Al contribuir, aceptas que tus contribuciones estarán bajo la misma licencia MIT del proyecto.

---

**¡Gracias por contribuir!** 🍋✨

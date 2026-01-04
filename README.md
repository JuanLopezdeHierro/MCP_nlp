# 🏋️ Gym Assistant - Agente Conversacional con MCP

## ¿Qué es este proyecto?
Un **asistente de gimnasio** que usa inteligencia artificial para gestionar reservas de clases, integrado con **Google Calendar**.

---

## 📁 Estructura del Proyecto

```
GymAssistant/
├── agent.py           # Agente principal (CLI + OpenAI)
├── gym_server.py      # Servidor MCP con herramientas
├── calendar_service.py # Integración con Google Calendar
├── bookings.json      # Base de datos de clases (JSON)
├── requirements.txt   # Dependencias Python
└── run_agent.bat      # Script para ejecutar
```

---

## 🔧 Tecnologías Utilizadas

| Tecnología | Uso |
|------------|-----|
| **FastMCP** | Define las herramientas que el LLM puede usar |
| **OpenAI API** | Modelo de lenguaje (gpt-4o) para conversación |
| **Google Calendar API** | Integración con calendario externo |
| **Python** | Lenguaje de programación |

---

## 🧠 ¿Cómo Funciona?

### 1. El usuario escribe un mensaje
```
"Reserva Yoga para María y ponlo en mi calendario"
```

### 2. OpenAI analiza el mensaje y decide qué herramienta usar
```python
# OpenAI devuelve:
tool_call: book_and_add_to_calendar(class_name="Yoga", user_name="María")
```

### 3. El agente ejecuta la herramienta MCP
```python
# gym_server.py ejecuta la función
result = book_and_add_to_calendar("Yoga", "María")
```

### 4. El resultado vuelve a OpenAI para generar respuesta
```
"He reservado Yoga para María y lo he añadido a tu calendario."
```

---

## 🔨 Herramientas MCP Definidas

### Herramientas Locales (gym_server.py)
```python
@mcp.tool()
def list_classes() -> str:
    """Lista las clases disponibles"""

@mcp.tool()
def book_class(class_name: str, user_name: str) -> str:
    """Reserva una clase para un usuario"""

@mcp.tool()  
def cancel_booking(class_name: str, user_name: str) -> str:
    """Cancela una reserva"""

@mcp.tool()
def get_my_bookings(user_name: str) -> str:
    """Muestra las reservas de un usuario"""
```

### Herramientas Externas (Google Calendar)
```python
@mcp.tool()
def view_calendar(max_events: int) -> str:
    """Muestra eventos del calendario de Google"""

@mcp.tool()
def add_class_to_calendar(class_name: str, user_name: str) -> str:
    """Añade un evento al calendario"""

@mcp.tool()
def book_and_add_to_calendar(class_name: str, user_name: str) -> str:
    """Reserva Y añade al calendario"""
```

---

## 📊 Flujo de Datos

```
Usuario → agent.py → OpenAI API → Decide herramienta
                         ↓
                    gym_server.py → Ejecuta herramienta
                         ↓
                    bookings.json (datos locales)
                         ↓
                    calendar_service.py → Google Calendar API
                         ↓
                    Respuesta al usuario
```

---

## 🚀 Cómo Ejecutar

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar el agente
python agent.py
# o usar: .\run_agent.bat
```

---

## 📝 Ejemplo de Conversación

```
User: Hola, ¿qué clases hay?
[Tool Call] list_classes()
Assistant: Tenemos Yoga, Pilates, CrossFit, Spinning...

User: Reserva Spinning para Juan
[Tool Call] book_class("Spinning", "Juan")
Assistant: Reservado Spinning para Juan.

User: Muéstrame mi calendario
[Tool Call] view_calendar(5)
Assistant: Tienes: Médico lunes, Spinning miércoles...
```

---

## ✅ Requisitos Cumplidos

- [x] Agente conversacional basado en LLM (OpenAI)
- [x] Gestión de diálogo (mantiene contexto)
- [x] Herramientas MCP propias (4 herramientas locales)
- [x] Integración MCP público (Google Calendar - 3 herramientas)
- [x] CLI interactivo con logs de herramientas

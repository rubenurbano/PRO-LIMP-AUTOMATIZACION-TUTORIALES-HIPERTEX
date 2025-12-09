README_MCP_Server.txt# README_MCP_Server.txt
# ---------------------------------------------
# Proyecto: ServidorMCP_Ruben
# Archivo principal: mcp_server.py
# Librería: fastmcp 2.13.0.2
# ---------------------------------------------

## ¿Qué es este script?
Este archivo lanza un **servidor MCP local** usando la librería `fastmcp`.
El protocolo MCP (Model Context Protocol) permite que **agentes de IA (ChatGPT, Claude, Gemini, etc.)**
puedan comunicarse con herramientas externas, programas o servicios creados por ti.

En este caso, `mcp_server.py` define dos herramientas:
1. `get_time()` → devuelve la fecha y hora actual del sistema.
2. `hola(nombre)` → devuelve un saludo personalizado.

## ¿Cómo se ejecuta?
1. Abrir PowerShell en la carpeta:

C:\Users\rubenurbano\HIPERTEX
2. Ejecutar:

python mcp_server.py
3. Si todo está bien, verás:

Starting MCP server 'ServidorMCP_Ruben' with transport 'stdio'
Eso significa que el servidor está **corriendo y esperando clientes**.

4. Para detenerlo, pulsa:

Ctrl + C

## ¿Qué significa "Transport: STDIO"?
- El servidor se comunica por el flujo estándar de entrada/salida (STDIO).
- Esto quiere decir que **no abre un puerto web ni muestra interfaz**.
- Solo responderá a programas compatibles con MCP (por ejemplo, ChatGPT con el módulo MCP Toolkit o Claude Desktop).




## Próximos pasos recomendados
- Crear un cliente local (`mcp_client_test.py`) para llamar a las herramientas desde Python.
- O integrar este servidor con el **MCP Toolkit de ChatGPT** para que Orion pueda usarlo como herramienta directa.
- En una segunda etapa, contenedizarlo con **Docker** (imagen base: `python:3.13-slim`) para facilitar el despliegue.

## Estado actual
✅ Librería fastmcp instalada correctamente  
✅ Servidor MCP funcional en modo STDIO  
⚙️ Pendiente: cliente o integración con ChatGPT MCP Toolkit

# Rubén Urbano – HIPERTEX – 08/11/2025
*****************************************************************


*******Uso:


Asegúrate de tener mcp_server.py ejecutándose (no lo cierres).


En otra consola PowerShell, en la misma carpeta (HIPERTEX), ejecuta:
python mcp_client_test.py



Deberías ver algo como:
🕒 Ejecutando get_time():
 → 2025-11-08 17:45:00

👋 Ejecutando hola('Rubén'):
 → Hola Rubén, soy tu primer servidor MCP!



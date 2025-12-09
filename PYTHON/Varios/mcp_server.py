# mcp_server.py
# -----------------------------------------------------------
# Servidor MCP local de Rubén utilizando FastMCP
# Versión: 2.13.0.2
# -----------------------------------------------------------

from fastmcp import FastMCP
from datetime import datetime
import json

# -----------------------------------------------------------
# Crear el servidor MCP y cargar el manifest manualmente
# -----------------------------------------------------------
app = FastMCP("ServidorMCP_Ruben")

# Cargar el manifest.json (solo informativo)
try:
    with open("manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
        print(f"📄 Manifest cargado: {manifest['name']} con {len(manifest['tools'])} herramientas.")
except Exception as e:
    print("⚠️ No se pudo cargar el manifest.json:", e)

# -----------------------------------------------------------
# Herramienta 1: hola(nombre)
# -----------------------------------------------------------
@app.tool()
def hola(nombre: str) -> str:
    """Devuelve un saludo personalizado."""
    return f"¡Hola, {nombre}! Soy tu servidor MCP local, encantado de saludarte."


# -----------------------------------------------------------
# Herramienta 2: get_time()
# -----------------------------------------------------------
@app.tool()
def get_time() -> str:
    """Devuelve la fecha y hora actual."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# -----------------------------------------------------------
# Punto de entrada
# -----------------------------------------------------------
if __name__ == "__main__":
    app.run()


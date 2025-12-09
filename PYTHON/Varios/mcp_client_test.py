# mcp_client_test.py
# ---------------------------------------------
# Cliente MCP minimalista para Rubén Urbano
# Prueba local de las herramientas del servidor ServidorMCP_Ruben
# Librería: fastmcp 2.13.0.2
# ---------------------------------------------

from fastmcp.client import FastMCPClient
import asyncio

async def main():
    # Crear cliente MCP local
    client = FastMCPClient("ServidorMCP_Ruben")

    # Conectarse al servidor (por STDIO local)
    # En esta demo, simulamos conexión directa (no remota)
    async with client.session():
        # Llamar a la herramienta get_time()
        print("🕒 Ejecutando get_time():")
        respuesta_hora = await client.call("get_time")
        print(" →", respuesta_hora)

        # Llamar a la herramienta hola(nombre)
        print("\n👋 Ejecutando hola('Rubén'):")
        respuesta_saludo = await client.call("hola", {"nombre": "Rubén"})
        print(" →", respuesta_saludo)

if __name__ == "__main__":
    asyncio.run(main())

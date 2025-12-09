# listar_gemini_modelos.py
# ----------------------------------------------------
# Lista todos los modelos Gemini disponibles en tu cuenta
# usando tu API Key de Google AI Studio.

from google import genai
import os

# Cargar la clave desde la variable de entorno
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ No se encontró la variable GOOGLE_API_KEY. Ejecuta en PowerShell: setx GOOGLE_API_KEY 'tu_api_key'")

# Crear el cliente autenticado
client = genai.Client(api_key=api_key)

print("\n📜 Modelos disponibles en tu cuenta:\n")

for modelo in client.models.list():
    print(f"- {modelo.name}")

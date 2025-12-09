from supabase import create_client
import os

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

# Insertar un contexto (usa listas → JSONB y arrays de texto)
nuevo = {
    "titulo": "Sesión Supabase OK",
    "objetivo_dia": "Probar conexión y preparar memoria de contextos",
    "errores": ["Editor SQL con 'Loading' infinito"],
    "causas": ["caché del navegador"],
    "soluciones": "Ctrl+F5 y reabrir SQL Editor; probar inserción desde Python",
    "pendientes": ["Conectar Gemini ↔ Supabase para guardar resúmenes"],
    "decisiones": "Guardar claves vía os.environ; usar tabla única flexible",
    "evidencias": ["commit://colab-pro-limp/docs", "issue://#12"],
    "etiquetas": ["supabase","python","gemini"],
    "fuente": "vscode",
}
supabase.table("contextos_orion").insert(nuevo).execute()

# Listar últimos contextos
resp = supabase.table("contextos_orion").select("*").order("fecha", desc=True).limit(5).execute()
print(resp.data)

from datetime import datetime, timezone
from supabase import create_client
import os
from datetime import datetime

# Conexión a Supabase (usa tus variables de entorno)
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

def guardar_contexto(titulo: str, resumen: str, etiquetas=None, fuente="orion"):
    """Guarda un contexto de chat en Supabase."""
    if etiquetas is None:
        etiquetas = ["orion", "chat"]

    data = {
        "fecha": datetime.now(timezone.utc).isoformat(),
        "titulo": titulo,
        "objetivo_dia": resumen,
        "etiquetas": etiquetas,
        "fuente": fuente,
    }

    try:
        supabase.table("contextos_orion").insert(data).execute()
        print("Contexto guardado correctamente.")
    except Exception as e:
        print("Error al guardar el contexto:", e)

# Ejemplo de uso
if __name__ == "__main__":
    guardar_contexto(
        titulo="Integración Supabase finalizada",
        resumen="Conexión validada, inserción correcta y tabla lista para registrar contextos.",
        etiquetas=["supabase", "python", "bitácora"]
    )

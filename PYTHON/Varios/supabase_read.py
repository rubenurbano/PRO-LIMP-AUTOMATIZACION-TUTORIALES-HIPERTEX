from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE = "pruebas"

def get_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Faltan SUPABASE_URL o SUPABASE_KEY (variables de entorno).")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    supabase = get_client()

    # Inserta una fila de prueba (borra si no quieres insertar)
    try:
        insert_resp = supabase.table(TABLE).insert({"nombre": "Hola PRO-LIMP"}).execute()
        print("✅ Insert:", insert_resp.data)
    except Exception as e:
        print("⚠️ Error al insertar (¿política de insert?):", e)

    # Lee las últimas 10 filas
    try:
        select_resp = supabase.table(TABLE).select("*").order("created_at", desc=True).limit(10).execute()
        rows = getattr(select_resp, "data", []) or []
        print(f"✅ Lectura: {len(rows)} fila(s)")
        for r in rows:
            print(r)
    except Exception as e:
        print("❌ Error al leer:", e)

if __name__ == "__main__":
    main()

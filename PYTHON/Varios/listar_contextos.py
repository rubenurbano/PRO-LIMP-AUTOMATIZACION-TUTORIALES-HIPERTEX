from supabase import create_client
import os

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

def listar_todos_contextos():
    try:
        resp = supabase.table("contextos_orion").select("*").order("fecha", desc=True).execute()
        data = resp.data or []
        print(f"Total de contextos: {len(data)}\n")
        for item in data:
            print(f"📅 {item.get('fecha')}")
            print(f"🧩 {item.get('titulo')}")
            if item.get('errores'):
                print(f"   Errores: {item.get('errores')}")
            if item.get('causas'):
                print(f"   Causas: {item.get('causas')}")
            if item.get('soluciones'):
                print(f"   Solución: {item.get('soluciones')}")
            print(f"   Etiquetas: {item.get('etiquetas')}\n")
    except Exception as e:
        print("Error al listar contextos:", e)

if __name__ == "__main__":
    listar_todos_contextos()

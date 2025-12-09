from supabase import create_client
import os

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

supabase.table("contextos_orion").insert({
    "titulo": "Prueba inicial Orion",
    "objetivo_dia": "Comprobar inserción en el esquema público"
}).execute()

print("Inserción correcta en public.contextos_orion")

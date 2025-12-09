from supabase import create_client, Client
from cryptography.fernet import Fernet
import os

# ======================
# CONFIGURACIÓN BÁSICA
# ======================

SUPABASE_URL = "https://wctqujwxwqrigsrimfpz.supabase.co"

# 👉 TU CLAVE service_role
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndjdHF1and4d3FyaWdzcmltZnB6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTAxMTY0OCwiZXhwIjoyMDgwNTg3NjQ4fQ.Dze4lPXJwD-iW9E5RnN3OWAhCnjinPCci_CprwQ5IIg"

BUCKET_NAME = "ntmnd-backups"

FERNET_KEY = os.environ["FERNET_KEY"].encode()
fernet = Fernet(FERNET_KEY)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# ======================
# FUNCIONES
# ======================

def encrypt_and_upload(local_path: str, remote_path: str) -> None:
    """Cifra un archivo local y lo sube cifrado a Supabase Storage."""

    # Leer archivo original
    with open(local_path, "rb") as f:
        plaintext = f.read()

    # Cifrar
    ciphertext = fernet.encrypt(plaintext)

    # Guardar temporalmente
    temp_path = local_path + ".enc"
    with open(temp_path, "wb") as f:
        f.write(ciphertext)

    # Subir archivo cifrado
    with open(temp_path, "rb") as f:
        res = supabase.storage.from_(BUCKET_NAME).upload(
            path=remote_path,
            file=f,
            file_options={"content-type": "application/octet-stream", "x-upsert": "true"},
        )

    print("Subida completada:", res)


def download_and_decrypt(remote_path: str, output_path: str) -> None:
    """Descarga un archivo cifrado desde Supabase y lo descifra en local."""

    encrypted_bytes = supabase.storage.from_(BUCKET_NAME).download(remote_path)

    plaintext = fernet.decrypt(encrypted_bytes)

    with open(output_path, "wb") as f:
        f.write(plaintext)

    print("Archivo descifrado en:", output_path)


# ======================
# EJEMPLO DE USO
# ======================

if __name__ == "__main__":
    encrypt_and_upload(
        local_path="secreto.pdf",
        remote_path="backups/secreto.pdf.enc"
    )

    download_and_decrypt(
        remote_path="backups/secreto.pdf.enc",
        output_path="secreto_descifrado.pdf"
    )

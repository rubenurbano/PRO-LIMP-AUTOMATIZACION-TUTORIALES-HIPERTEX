# organizar_hipertex_force_subfolders.py
# //copiable
# Organizador universal que:
# - Detecta/crea TEMA por token o palabras clave conocidas (si no encuentra: usa token dinámico).
# - Mueve archivos de la raíz a: ROOT / TEMA_EN_MAYUS / (HPTX | JSON | VARIOS)
# - GARANTIZA que en cada carpeta de TEMA existan las subcarpetas HPTX, JSON y VARIOS (aunque estén vacías).
# - Evita sobrescribir archivos (añade sufijo _1, _2, ...).
# Uso: python organizar_hipertex_force_subfolders.py

import os
import shutil
import re
from pathlib import Path

# --- Configuración ---
CATEGORIES_KEYWORDS = {
    "FASTAPI": ["FASTAPI", "API"],
    "PYTHON": ["PYTHON", "PY", "PIP", "CONDA", "JUPYTER"],
    "DOCKER": ["DOCKER", "CONTAINER"],
    "MAKE": ["MAKE", "MAKE.COM"],
    "GOOGLE": ["GOOGLE", "GEMINI", "APPS SCRIPT", "COLAB", "SHEETS", "GMAIL", "FIREBASE", "ANDROID"],
    "EXCEL": ["EXCEL", "XLSX"],
    "CHATGPT": ["CHATGPT", "GPT", "OPENAI"],
    "CLAUDE": ["CLAUDE", "ANTHROPIC"],
    "PERPLEXITY": ["PERPLEXITY"],
    "PIANO": ["PIANO", "ACORDES", "MUSIC"],
    "GIT": ["GIT", "GITHUB"],
    # añade más si quieres...
}

IGNORE_DIRS = {".git", "venv", "__pycache__", "node_modules", ".gemini", ".history"}
IGNORE_FILES = {"organizar_hipertex_force_subfolders.py", "organizar_hipertex.py", "organizar_hipertex_autocreate.py", "HIPERTEX_SETUP.ps1", "build_catalog.py", "catalog.json"}

# Subcarpetas obligatorias (en MAYÚSCULAS)
MANDATORY_SUBFOLDERS = ("HPTX", "JSON", "VARIOS")

# SPLIT_RE: separa un nombre usando espacios, guiones, puntos, paréntesis, corchetes, etc.
# Sirve para dividir el nombre del archivo en "tokens" (palabras sueltas).
SPLIT_RE = re.compile(r"[ _\-\.\[\]\(\)\+]+")

# HAS_LETTER_RE: detecta si un token contiene al menos UNA letra (incluye acentos y ñ).
# Evita tomar tokens que sean solo números.
HAS_LETTER_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")

# Explicación carácter por carácter de los dos regex:

# --- SPLIT_RE ---
# r"[ _\-\.\[\]\(\)\+]+"
# [ ... ]   → define un conjunto de caracteres permitidos para dividir (separadores).
#   espacio → divide por cualquier espacio.
#   _       → divide por guion bajo.
#   \-      → divide por guion normal (se escapa con \ para que no sea rango).
#   \.      → divide por punto.
#   \[ \]   → divide por corchetes (los corchetes se escapan porque son símbolos especiales).
#   \( \)   → divide por paréntesis (también escapados).
#   \+      → divide por signo + (se escapa porque + es especial en regex).
# +         → significa "uno o más" separadores consecutivos.
# Resultado: SPLIT_RE divide nombres de archivo en palabras usando cualquiera de esos símbolos.


# --- HAS_LETTER_RE ---
# r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]"
# [ ... ]   → conjunto de caracteres que se consideran "letras".
# A-Z       → letras mayúsculas ASCII.
# a-z       → letras minúsculas ASCII.
# ÁÉÍÓÚÜÑ   → letras mayúsculas con tildes/diéresis y Ñ.
# áéíóúüñ   → letras minúsculas con tildes/diéresis y ñ.
# No tiene + porque solo queremos verificar que existe al menos una letra.
# Resultado: HAS_LETTER_RE detecta tokens que contienen alguna letra real (no números puros).


# --- Funciones ---
def detect_known_category(filename_upper: str):
    for cat, keys in CATEGORIES_KEYWORDS.items():
        for k in keys:
            if k in filename_upper:
                return cat.upper()
    return None

def detect_theme_dynamic(filename: str) -> str:
    """
    Primero intenta categoría conocida. Si no encuentra, toma el primer token
    alfabético del nombre (sin extensión) y lo usa como TEMA.
    Resultado en MAYÚSCULAS. Si no hay token, devuelve 'OTROS'.
    """
    name = Path(filename).stem
    name_up = filename.upper()
    known = detect_known_category(name_up)
    if known:
        return known
    tokens = SPLIT_RE.split(name)
    for t in tokens:
        if t and HAS_LETTER_RE.search(t):
            return t.upper()
    return "OTROS"

def map_extension_to_type(ext: str) -> str:
    ext = ext.lower()
    if ext == ".hptx":
        return "HPTX"
    if ext == ".json":
        return "JSON"
    return "VARIOS"

def safe_move(src: Path, dest_dir: Path):
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if not dest.exists():
        shutil.move(str(src), str(dest))
        return dest
    # si existe, agrega sufijo incremental
    base = src.stem
    ext = src.suffix
    i = 1
    while True:
        candidate = dest_dir / f"{base}_{i}{ext}"
        if not candidate.exists():
            shutil.move(str(src), str(candidate))
            return candidate
        i += 1

def ensure_mandatory_subfolders_for_theme(theme_dir: Path):
    """
    Asegura que dentro de theme_dir existan las subcarpetas MANDATORY_SUBFOLDERS
    (crea si faltan). Los nombres se crean en MAYÚSCULAS tal como está en la tupla.
    """
    for sub in MANDATORY_SUBFOLDERS:
        p = theme_dir / sub
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)

def enforce_mandatory_subfolders(root: Path):
    """
    Recorre todas las carpetas de primer nivel en root (excluyendo IGNORE_DIRS)
    y asegura que tengan HPTX, JSON y VARIOS.
    """
    for item in root.iterdir():
        if item.is_dir() and item.name not in IGNORE_DIRS:
            ensure_mandatory_subfolders_for_theme(item)

def organize(root_path: str):
    root = Path(root_path).resolve()
    if not root.exists() or not root.is_dir():
        print("ERROR: la ruta indicada no existe o no es una carpeta.")
        return

    # Primero asegurar que cualquier carpeta TEMA ya existente tenga las subcarpetas obligatorias
    enforce_mandatory_subfolders(root)

    # Listar archivos en la raíz (no recursivo)
    entries = list(root.iterdir())
    files = [p for p in entries if p.is_file() and p.name not in IGNORE_FILES]

    if not files:
        print("No se encontraron archivos a organizar en la raíz indicada.")
        return

    moved = 0
    for f in files:
        if f.name.startswith("."):
            continue
        theme = detect_theme_dynamic(f.name)  # devuelve en MAYÚSCULAS
        type_folder = map_extension_to_type(f.suffix)
        dest_dir = root / theme / type_folder  # ejemplo: C:\...\HIPERTEX\MAKE\JSON
        try:
            final = safe_move(f, dest_dir)
            # Asegurar las subcarpetas en el tema (por si la carpeta tema era nueva)
            ensure_mandatory_subfolders_for_theme(root / theme)
            print(f"MOVIDO: {f.name} → {theme}/{type_folder}  ({final.name})")
            moved += 1
        except Exception as e:
            print(f"ERROR moviendo {f.name}: {e}")

    # Una pasada final por si quedaron temas sin las subcarpetas obligatorias
    enforce_mandatory_subfolders(root)
    print(f"\nTerminado. Archivos procesados: {moved}")

# --- Entrada principal ---
if __name__ == "__main__":
    print("=== ORGANIZADOR (CON SUBCARPETAS OBLIGATORIAS: HPTX, JSON, VARIOS) ===")
    folder = input("Ruta completa de la carpeta a organizar:\n> ").strip()
    organize(folder)

# organize_files.py
# //copiable
# Script para organizar C:\Users\rubenurbano\HIPERTEX por TEMA > TIPO_DE_ARCHIVO
# Reglas:
# - Detecta la "palabra clave" del tema en el nombre del archivo (ej: Make, Perplexity).
#   Implementación práctica: toma el primer token significativo del nombre de archivo
#   (separadores: espacio, underscore, dash, punto). Si no hay token alfabético, usa 'OTROS'.
# - Para cada tema crea subcarpetas normalizadas a MAYÚSCULAS:
#     HPTX   -> para .hptx
#     JSON   -> para .json
#     VARIOS -> para cualquier otra extensión
# - Mueve los ficheros respetando la estructura: ROOT/TEMA/TIPO/archivo
# - Evita sobrescribir: si existe el fichero destino, añade sufijo _1, _2, ...
# - Funciona en Windows (usa rutas absolutas); se puede adaptar a otro root pasando --root.
# - Uso: python organize_files.py
#   Opciones:
#     --root "C:\ruta\a\carpeta"   : cambiar carpeta raíz (por defecto la solicitada)
#     --dry-run                     : listar cambios sin mover
#     --verbose                     : salida detallada

import os
import shutil
import argparse
import re
from pathlib import Path

DEFAULT_ROOT = r"C:\Users\rubenurbano\HIPERTEX"

# Tipos mapeados (carpetas en MAYÚSCULAS)
EXT_MAP = {
    ".hptx": "HPTX",
    ".json": "JSON"
}
DEFAULT_TYPE = "VARIOS"
FALLBACK_THEME = "OTROS"

TOKEN_SPLIT_RE = re.compile(r"[ _\-\.\[\]\(\)]+")  # separadores comunes
HAS_LETTER_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")  # para detectar token con letras

def detect_theme(filename: str) -> str:
    """
    Detecta el tema tomando el primer token significativo (alfabético) del nombre sin extensión.
    Normaliza a MAYÚSCULAS. Si no encuentra token válido, devuelve 'OTROS'.
    Ejemplos:
      "Make_http_log.txt" -> "MAKE"
      "2025-07-01_Perplexity-result.json" -> "PERPLEXITY"
      "12345.log" -> "OTROS"
    """
    name = Path(filename).stem  # sin extensión
    tokens = TOKEN_SPLIT_RE.split(name)
    for tok in tokens:
        if not tok:
            continue
        # ignorar tokens que son puramente numéricos
        if tok.isdigit():
            continue
        # preferir tokens que contengan al menos una letra
        if HAS_LETTER_RE.search(tok):
            return tok.upper()
    return FALLBACK_THEME

def map_extension_to_type(ext: str) -> str:
    """
    Mapea la extensión a la carpeta tipo (en MAYÚSCULAS).
    """
    ext_l = ext.lower()
    return EXT_MAP.get(ext_l, DEFAULT_TYPE)

def safe_move(src_path: Path, dest_dir: Path, dry_run=False) -> Path:
    """
    Mueve src_path a dest_dir, evitando sobrescrituras. Devuelve la ruta destino final (Path).
    Si dry_run=True no realiza movimientos, solo calcula la ruta destino.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src_path.name
    if not dest.exists():
        if not dry_run:
            shutil.move(str(src_path), str(dest))
        return dest
    # si existe, crea sufijo incremental
    base = src_path.stem
    ext = src_path.suffix
    counter = 1
    while True:
        new_name = f"{base}_{counter}{ext}"
        candidate = dest_dir / new_name
        if not candidate.exists():
            if not dry_run:
                shutil.move(str(src_path), str(candidate))
            return candidate
        counter += 1

def organize_folder(root: Path, dry_run=False, verbose=False):
    """
    Recorre únicamente los archivos (no entra en subcarpetas) en la carpeta `root`
    y los organiza según las reglas.
    """
    if not root.exists():
        raise FileNotFoundError(f"El directorio raíz no existe: {root}")

    # Recorremos sólo items de primer nivel (archivos). No tocamos subdirectorios.
    entries = list(root.iterdir())
    files = [p for p in entries if p.is_file()]
    if verbose:
        print(f"Encontrados {len(files)} archivos en {root}")

    moved_count = 0
    for f in files:
        theme = detect_theme(f.name)
        type_folder = map_extension_to_type(f.suffix)
        dest_dir = root / theme.upper() / type_folder  # normalizar tema a MAYÚSCULAS (ya lo es) y tipo también
        if verbose:
            print(f"{f.name} -> Tema: {theme.upper()} / Tipo: {type_folder}  -> Dest: {dest_dir}")

        final_path = safe_move(f, dest_dir, dry_run=dry_run)
        moved_count += 1

        if verbose:
            print(f"  {'(dry)' if dry_run else 'Movido'} -> {final_path}")

    if verbose:
        print(f"Procesados: {len(files)} archivos. Movidos (o listados en dry-run): {moved_count}")

def main():
    parser = argparse.ArgumentParser(description="Organiza archivos en carpetas por TEMA > TIPO (HPTX/JSON/VARIOS).")
    parser.add_argument("--root", type=str, default=DEFAULT_ROOT, help="Carpeta raíz a organizar.")
    parser.add_argument("--dry-run", action="store_true", help="Simular acciones sin mover archivos.")
    parser.add_argument("--verbose", action="store_true", help="Mostrar salida detallada.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    try:
        organize_folder(root, dry_run=args.dry_run, verbose=args.verbose)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()

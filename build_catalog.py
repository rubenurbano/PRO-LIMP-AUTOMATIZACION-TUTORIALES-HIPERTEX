#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
build_catalog.py — HIPERTEX HUB catalog builder
-----------------------------------------------
Genera un catálogo JSON de todos los archivos .hptx en una carpeta.

Uso (Windows / PowerShell):
  py build_catalog.py                            # escanea la carpeta actual y crea catalog.json
  py build_catalog.py --root "C:\Users\rubenurbano\HIPERTEX"
  py build_catalog.py --root . --recursive
  py build_catalog.py --root . --out my_catalog.json

Requisitos: NO requiere dependencias externas.
Formato soportado: HIPERTEX v1.0 (.hptx)

Salida (catalog.json):
{
  "hub": {
    "name": "HIPERTEX HUB",
    "generated_at": "2025-11-03T10:20:00Z",
    "base_path": "."
  },
  "tutorials": [
    {
      "file": "ejemplo HPTX.hptx",
      "relpath": "ejemplo HPTX.hptx",
      "size_bytes": 1234,
      "mtime": "2025-11-03T09:50:12Z",
      "title": "Tutorial Hipertex – Prueba de Concepto",
      "created": "2025-11-03",
      "tags": ["hipertex","parser","html","prueba"],
      "items_count": 3,
      "menu_count": 2
    }
  ]
}
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

# ---------- Utilidades ----------
def iso8601(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def utcnow_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

# ---------- Parsers HIPERTEX (ligeros) ----------
META_RE = re.compile(r"##HIPERTEX-META BEGIN([\s\S]*?)##HIPERTEX-META END", re.M)
ITEM_RE = re.compile(r"^##itemID:(.+)$", re.M)
MENU_RE = re.compile(r"##menu-item BEGIN([\s\S]*?)##menu-item END", re.M)

def parse_meta(src: str) -> dict:
    m = META_RE.search(src)
    if not m:
        return {}
    block = m.group(1).strip()
    meta = {}
    for line in block.splitlines():
        # elimina comentarios tipo YAML (# ...) y recorta
        line = re.sub(r"^\s*#.*$", "", line).strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta

def count_items(src: str) -> int:
    return len(list(ITEM_RE.finditer(src.replace("\r\n", "\n"))))

def count_menu(src: str) -> int:
    return len(list(MENU_RE.finditer(src)))

# ---------- Catálogo ----------
def scan_hptx(root: str, recursive: bool) -> list:
    items = []
    if recursive:
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                if name.lower().endswith(".hptx"):
                    items.append(os.path.join(dirpath, name))
    else:
        for name in os.listdir(root):
            if name.lower().endswith(".hptx"):
                items.append(os.path.join(root, name))
    return sorted(items)

def build_entry(path: str, root: str) -> dict:
    src = read_text(path)
    meta = parse_meta(src)

    stat = os.stat(path)
    relpath = os.path.relpath(path, root).replace("\\", "/")

    title = meta.get("title") or os.path.basename(path)
    created = meta.get("created") or ""
    tags_raw = meta.get("tags") or ""
    # Extrae lista simple de tags si vienen en formato [a, b, c] o "a, b, c"
    tags = []
    tr = tags_raw.strip()
    if tr.startswith("[") and tr.endswith("]"):
        tr = tr.strip("[]")
        tags = [t.strip().strip('"').strip("'") for t in tr.split(",") if t.strip()]
    elif tr:
        tags = [t.strip() for t in tr.split(",") if t.strip()]

    entry = {
        "file": os.path.basename(path),
        "relpath": relpath,
        "size_bytes": stat.st_size,
        "mtime": iso8601(stat.st_mtime),
        "title": title,
        "created": created,
        "tags": tags,
        "items_count": count_items(src),
        "menu_count": count_menu(src),
    }
    return entry

def write_catalog(data: dict, out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    ap = argparse.ArgumentParser(description="Genera un catálogo HIPERTEX HUB (catalog.json).")
    ap.add_argument("--root", default=".", help="Carpeta raíz a escanear (por defecto: .)")
    ap.add_argument("--recursive", action="store_true", help="Buscar .hptx recursivamente")
    ap.add_argument("--out", default="catalog.json", help="Ruta del JSON de salida (por defecto: catalog.json)")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    files = scan_hptx(root, args.recursive)

    tutorials = []
    for p in files:
        try:
            tutorials.append(build_entry(p, root))
        except Exception as e:
            # No abortamos el catálogo por un archivo defectuoso
            tutorials.append({
                "file": os.path.basename(p),
                "relpath": os.path.relpath(p, root).replace("\\", "/"),
                "error": str(e)
            })

    catalog = {
        "hub": {
            "name": "HIPERTEX HUB",
            "generated_at": utcnow_iso(),
            "base_path": os.path.relpath(root, root) or ".",
            "count": len(tutorials)
        },
        "tutorials": tutorials
    }

    write_catalog(catalog, args.out)
    print(f"[OK] Catálogo generado: {args.out}  (total: {len(tutorials)})")

if __name__ == "__main__":
    main()

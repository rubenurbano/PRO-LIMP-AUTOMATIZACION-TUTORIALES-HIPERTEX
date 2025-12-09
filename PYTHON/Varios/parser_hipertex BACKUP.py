#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Parser HIPERTEX v2.1 — compatible con Windows UTF-8
----------------------------------------------------
Uso (Windows / PowerShell):
  pip install python-docx charset-normalizer
  py parser_hipertex.py input.hptx
  py parser_hipertex.py input.txt
  py parser_hipertex.py input.docx
"""
import sys, os, json, re
from charset_normalizer import from_path

# ---------- Lectura universal con detección ----------
def read_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()

    if ext in ('.hptx', '.txt'):
        try:
            result = from_path(path).best()
            return str(result)
        except Exception as e:
            sys.stderr.write(f"[WARN] Error detectando codificación: {e}\n")
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()

    elif ext == '.docx':
        try:
            from docx import Document
        except ImportError:
            sys.stderr.write("Falta dependencia: python-docx (instala con: pip install python-docx)\n")
            sys.exit(2)
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        sys.stderr.write(f"Extensión no soportada: {ext}\n")
        sys.exit(2)

# ---------- Parsing HIPERTEX ----------
META_RE = re.compile(r"##HIPERTEX-META BEGIN([\s\S]*?)##HIPERTEX-META END", re.M)
ITEM_RE = re.compile(r"^##itemID:(.+)$", re.M)
MENU_RE = re.compile(r"##menu-item BEGIN([\s\S]*?)##menu-item END", re.M)
CONT_RE = re.compile(r"##Contenido BEGIN([\s\S]*?)##Contenido END", re.M)

def parse_meta(src: str):
    m = META_RE.search(src)
    if not m:
        return {}, src
    block = m.group(1).strip()
    meta = {}
    for line in block.splitlines():
        line = re.sub(r"^\s*#.*$", "", line).strip()
        if not line:
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    rest = src[:m.start()] + src[m.end():]
    return meta, rest

def sanitize_id(raw: str) -> str:
    return re.sub(r"[^\w\-]", "_", str(raw).strip())

def strip_one_newline(s: str) -> str:
    return re.sub(r"^\n|\n$", "", s)

def parse_blocks(src: str):
    src = src.replace("\r\n", "\n").replace("\r", "\n")
    items = []
    matches = list(ITEM_RE.finditer(src))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(src)
        id_raw = m.group(1).strip()
        block = src[start:end]

        menu_m = MENU_RE.search(block)
        menu_item = strip_one_newline(menu_m.group(1)) if menu_m else None

        cont_ms = list(CONT_RE.finditer(block))
        contenido = "\n".join(strip_one_newline(cm.group(1)) for cm in cont_ms) if cont_ms else ""

        items.append({
            "itemID_raw": id_raw,
            "itemID": sanitize_id(id_raw),
            "menu_item": menu_item,
            "contenido": contenido
        })

    seen = {}
    for it in items:
        base = it["itemID"]
        k = base
        n = 2
        while k in seen:
            k = f"{base}-{n}"
            n += 1
        seen[k] = True
        it["itemID"] = k
    return items

def parse_hipertex(src: str):
    meta, rest = parse_meta(src)
    return {"meta": meta, "items": parse_blocks(rest)}

# ---------- Main ----------
def main():
    if len(sys.argv) < 2:
        print("Uso: py parser_hipertex.py <archivo.hptx|.txt|.docx>")
        sys.exit(1)

    path = sys.argv[1]
    src = read_text(path)
    data = parse_hipertex(src)

    # 🔥 Salida forzada a archivo UTF-8
    out_file = os.path.splitext(os.path.basename(path))[0] + "_parsed.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Archivo guardado como {out_file} (UTF-8 ✅)")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Parser HIPERTEX v3.1 — IDs limpios (000...), sin itemID_raw, y soporte sin menú
-------------------------------------------------------------------------------
Uso (Windows / PowerShell):
  py -m pip install python-docx charset-normalizer
  py parser_hipertex.py input.hptx
  py parser_hipertex.py input.txt
  py parser_hipertex.py input.docx
"""
import sys, os, json, re
from charset_normalizer import from_path

# ------------------------- Lectura universal -------------------------
def read_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.hptx', '.txt'):
        try:
            # Priorizar utf-8-sig para manejar BOMs de forma nativa
            with open(path, 'r', encoding='utf-8-sig') as f:
                return f.read()
        except (UnicodeDecodeError, TypeError) as e:
            sys.stderr.write(f"[WARN] Lectura como UTF-8 (con/sin BOM) falló: {e}\n")
            # Fallback a UTF-8 con reemplazo de errores
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            sys.stderr.write(f"[WARN] Detección de codificación falló: {e}\n")
            # Fallback a la detección automática si la lectura directa falla
            try:
                best = from_path(path).best()
                return str(best)
            except Exception as e_inner:
                sys.stderr.write(f"[ERROR] Falló la detección de codificación: {e_inner}\n")
                # Fallback final a lectura con reemplazo
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
    elif ext == '.docx':
        try:
            from docx import Document
        except ImportError:
            sys.stderr.write("Falta dependencia: python-docx (instala con: py -m pip install python-docx)\n")
            sys.exit(2)
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        sys.stderr.write(f"Extensión no soportada: {ext}\n")
        sys.exit(2)

# ---------------------------- Expresiones ----------------------------
META_RE = re.compile(r"##HIPERTEX-META BEGIN([\s\S]*?)##HIPERTEX-META END", re.M)
ITEM_RE = re.compile(r"^##itemID:(.+)$", re.M)
MENU_RE = re.compile(r"##menu-item BEGIN([\s\S]*?)##menu-item END", re.M)
CONT_RE = re.compile(r"##Contenido BEGIN([\s\S]*?)##Contenido END", re.M)

# ---------------------------- Utilidades -----------------------------
def sanitize_id(raw: str) -> str:
    # Mantiene dígitos/guiones/underscore; quita espacios y raro
    return re.sub(r"[^\w\-]", "_", str(raw).strip())

def strip_one_newline(s: str) -> str:
    # Quita solo UN salto de línea al borde
    return re.sub(r"^\n|\n$", "", s)

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

# ------------------------- Parsing principal -------------------------
def parse_blocks(src: str):
    """
    Reglas:
    - Si hay ##itemID:..., cada bloque es [##itemID ... (hasta próximo ID o EOF)].
      • menu_item puede faltar (queda None).
      • contenido puede existir (uno o varios ##Contenido) o faltar ("").
      • itemID se respeta tal cual (sanitizado). No se inventa título.
    - Si NO hay ##itemID en absoluto:
      • se crean items a partir de cada ##Contenido, numerando itemID como 000, 001, ...
    """
    src = src.replace("\r\n", "\n").replace("\r", "\n")
    items = []
    matches = list(ITEM_RE.finditer(src))

    if matches:
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(src)
            id_text = m.group(1).strip()
            block = src[start:end]

            # Título del menú (opcional)
            menu_m = MENU_RE.search(block)
            menu_item = strip_one_newline(menu_m.group(1)) if menu_m else None

            # Contenido (0..n) — concatenado con salto
            cont_ms = list(CONT_RE.finditer(block))
            contenido = "\n".join(strip_one_newline(cm.group(1)) for cm in cont_ms) if cont_ms else ""

            items.append({
                "itemID": sanitize_id(id_text),
                "menu_item": menu_item,
                "contenido": contenido
            })
    else:
        # No hay IDs: cada Contenido es un item; IDs autogenerados 000...
        cont_ms = list(CONT_RE.finditer(src))
        for i, cm in enumerate(cont_ms):
            contenido = strip_one_newline(cm.group(1))
            items.append({
                "itemID": f"{i:03}",
                "menu_item": None,
                "contenido": contenido
            })

    # Garantizar unicidad de itemID en caso de duplicados accidentales
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

    # Filtrado opcional: mantener ítems con algo que mostrar (contenido o título)
    # (Si prefieres conservar absolutamente todos, comenta el return siguiente y descomenta el de abajo)
    filtered = [it for it in items if (it.get("menu_item") or (it.get("contenido") and it["contenido"].strip()))]
    return filtered
    # return items

def parse_hipertex(src: str):
    meta, rest = parse_meta(src)
    return {"meta": meta, "items": parse_blocks(rest)}

# ------------------------------- Main --------------------------------
def main():
    if len(sys.argv) < 2:
        print("Uso: py parser_hipertex.py <archivo.hptx|.txt|.docx>")
        sys.exit(1)

    path = sys.argv[1]
    src = read_text(path)
    data = parse_hipertex(src)

    out_file = os.path.splitext(os.path.basename(path))[0] + "_parsed.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Archivo guardado como {out_file} (UTF-8 ✅)")

if __name__ == "__main__":
    main()

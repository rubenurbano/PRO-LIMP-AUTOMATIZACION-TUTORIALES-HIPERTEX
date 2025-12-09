#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generador de tutoriales HPTX + JSON para HIPERTEX usando Gemini 2.5.

Entradas:
- TÍTULO del vídeo / contenido (usado para:
    - Nombre del archivo .txt de transcripción
    - Contenido del bloque 000
    - Nombre de salida .hptx y .json)

Transcripción (NotebookLM o lo que uses):
- Se busca automáticamente en la carpeta actual con estos nombres, en este orden:
    1) "<TITULO>.txt"
    2) "<TITULO_SAFE>.txt"
       (mismo título pero sin caracteres ilegales de Windows, como < > : " / \\ | ? *)
    3) "<slug-del-titulo>.txt"
       (ejemplo: "tutorial-del-agente-de-ia-de-make-com-integracion-perfecta-de-claude-con-dropbox.txt")

- Si se encuentra y tiene contenido → se usa como base factual.
- Si no se encuentra → se genera sin transcripción (solo con el título).

Salida:
- <slug>.hptx  -> texto HPTX con tus tags.
- <slug>.json  -> { "meta": {}, "items": [ ... ] }
"""

import re
import json
from pathlib import Path

from google import genai


# ========================
#  UTILIDADES
# ========================

def slugify(text: str) -> str:
    """Convierte un título en un nombre de archivo sencillo."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "tutorial"


def title_candidates_to_txt(titulo: str) -> list[Path]:
    """
    Genera candidatos de nombres de archivo .txt basados en el título:
      1) "<TITULO>.txt"
      2) "<TITULO_SAFE>.txt" (sin caracteres ilegales de Windows)
      3) "<slug-del-titulo>.txt"
    """
    candidates: list[Path] = []

    # 1) Título exacto
    candidates.append(Path(f"{titulo}.txt"))

    # 2) Versión "safe" para Windows (quitamos caracteres ilegales)
    safe_title = re.sub(r'[<>:"/\\|?*]', "", titulo).strip()
    if safe_title and safe_title != titulo:
        candidates.append(Path(f"{safe_title}.txt"))

    # 3) Slug
    slug = slugify(titulo)
    candidates.append(Path(f"{slug}.txt"))

    # Eliminar duplicados manteniendo orden
    seen = set()
    unique: list[Path] = []
    for p in candidates:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return unique


def get_transcript_from_txt_by_title(titulo: str) -> str:
    """
    Busca un archivo .txt basado en el título:
      "<TITULO>.txt" / "safe.txt" / "slug.txt"
    en la carpeta actual. Si encuentra uno no vacío, devuelve su contenido.
    """
    candidates = title_candidates_to_txt(titulo)

    for path in candidates:
        if path.exists() and path.is_file():
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").strip()
                if text:
                    print(f"📄 Usando transcripción desde archivo: {path.name}")
                    return text
                else:
                    print(f"⚠ El archivo {path.name} está vacío.")
            except Exception as e:
                print(f"⚠ Error leyendo {path.name}: {e}")

    print("ℹ No se encontró ningún .txt de transcripción para este título.")
    return ""


def obtener_transcripcion(titulo: str) -> str:
    """
    Lógica de transcripción:
    1) Busca .txt basado en el título.
    2) Si no encuentra nada, devuelve "" (se trabaja solo con el título).
    """
    transcript = get_transcript_from_txt_by_title(titulo)
    if transcript:
        return transcript

    print("ℹ Se continuará sin transcripción (solo con el título).")
    return ""


# ========================
#  PROMPT HPTX
# ========================

def build_prompt_hptx(titulo: str, transcript: str | None) -> str:
    if transcript:
        transcript_section = f"""A continuación tienes la TRANSCRIPCIÓN del contenido (o parte de ella).
Utiliza esta transcripción como base factual para el tutorial. Puedes reordenar, resumir y aclarar,
pero no inventes contenidos que la contradigan claramente.

=== TRANSCRIPCIÓN BEGIN ===
{transcript}
=== TRANSCRIPCIÓN END ===
"""
    else:
        transcript_section = (
            "⚠ No se ha podido proporcionar una transcripción.\n"
            "Genera el tutorial utilizando sentido común a partir del título y del tema, "
            "pero sé claro y honesto en las explicaciones.\n"
        )

    prompt = f"""
Escribe un tutorial completo con el siguiente título y estructura, respetando EXACTAMENTE
los tags y el formato HPTX que se indica.

TÍTULO:
"{titulo}"

{transcript_section}

### FORMATO BASE HPTX (OBLIGATORIO):

Cada sección del tutorial debe seguir este esquema EXACTO:

##itemID: 000
##menu-item BEGIN
[Título o descripción del paso]
##menu-item END
##Contenido BEGIN
[Título o descripción del paso]:

[Desarrollo detallado del paso]
##Contenido END

REGLAS DEL FORMATO:

1. "##itemID:" siempre seguido de un número de 3 dígitos: 000, 001, 002, ...
2. Entre "##Contenido END" y el siguiente "##itemID:" debe haber SIEMPRE una línea en blanco.
3. El documento completo se compone de muchos bloques consecutivos con esa estructura.
4. No añadas texto fuera de esa estructura; todo debe estar dentro de bloques HPTX.
5. No uses Markdown, ni ``` ni JSON. SOLO texto plano con tags HPTX.

### ESTRUCTURA ESPECÍFICA OBLIGATORIA:

1. El PRIMER bloque (##itemID: 000) DEBE SER EXACTAMENTE ESTE FORMATO:

##itemID: 000
##menu-item BEGIN
{titulo}
WEB ORIGINAL:
##menu-item END
##Contenido BEGIN
{titulo}:
Web Original:

{titulo}
(Sin URL disponible)
##Contenido END

2. A partir de ##itemID: 001:
   - Divide el contenido en pasos claros y progresivos.
   - Cada "##menu-item" debe ser un título breve del paso.
   - Cada "##Contenido" debe explicar ese paso en detalle.

3. El ÚLTIMO bloque del documento debe tener:
   - ##menu-item BEGIN
     VALIDACIÓN CON FUENTES TÉCNICAS OFICIALES
   - En "##Contenido":
     - Resumen de los puntos clave del tutorial.
     - Lista de referencias o fuentes técnicas reales o razonables
       (documentación oficial, manuales, documentación estándar del tema, etc.).

### REGLAS DE CONTENIDO:

1. Idioma: SIEMPRE ESPAÑOL, claro, directo y sin paja.
2. Público objetivo: usuarios sin conocimientos técnicos, pero inteligentes.
3. Cada bloque de contenido debe tener varios párrafos y, cuando sea útil, pasos numerados:
   1. Acción clara 1
   2. Acción clara 2
   3. Acción clara 3
4. Si se usa la transcripción:
   - Respeta el sentido del contenido.
   - Aclara, ordena, resume, pero no contradigas.
5. Si NO se ha podido obtener transcripción:
   - Genera un tutorial razonable basado en el tema, sin inventar datos técnicos falsos.

### SALIDA ESPERADA:

- Devuelve ÚNICAMENTE el contenido HPTX, empezando por:
  "##itemID: 000"
- No añadas comentarios, ni explicaciones fuera de los bloques HPTX.
- No uses markdown, ni ``` ni JSON.

Empieza ahora el tutorial HPTX:
"""

    return prompt


# ========================
#  GEMINI: GENERAR HPTX
# ========================

def generar_tutorial_hptx(titulo: str) -> str:
    client = genai.Client()

    transcript = obtener_transcripcion(titulo)
    prompt = build_prompt_hptx(titulo, transcript or None)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini devolvió una respuesta vacía.")

    return text


# ========================
#  PARSEAR HPTX → JSON
# ========================

def hptx_to_json(hptx_text: str) -> dict:
    pattern = re.compile(
        r"##itemID:\s*(\d{3})\s*[\r\n]+"
        r"##menu-item BEGIN\s*(.*?)\s*##menu-item END\s*"
        r"##Contenido BEGIN\s*(.*?)\s*##Contenido END",
        re.DOTALL | re.MULTILINE,
    )

    items = []
    for match in pattern.finditer(hptx_text):
        item_id = match.group(1).strip()
        menu_item = match.group(2).strip()
        contenido = match.group(3).strip()

        items.append(
            {
                "itemID": item_id,
                "menu_item": menu_item,
                "contenido": contenido,
            }
        )

    if not items:
        raise RuntimeError("No se encontraron bloques HPTX válidos en el texto.")

    data = {
        "meta": {},
        "items": items,
    }
    return data


# ========================
#  MAIN
# ========================

def main() -> None:
    print("=== Generador HPTX + JSON con Gemini 2.5 (genai) ===")
    raw_title = input("Título del vídeo / contenido: ").strip()

    if not raw_title:
        print("❌ El título es obligatorio.")
        return

    # Si el usuario mete el título con ".txt" al final, se lo quitamos
    titulo = raw_title
    if titulo.lower().endswith(".txt"):
        titulo = titulo[:-4].strip()

    print(f"📝 Título normalizado: {titulo}")

    print("🧠 Generando tutorial HPTX con Gemini...")
    hptx = generar_tutorial_hptx(titulo)

    slug = slugify(titulo)

    hptx_filename = f"{slug}.hptx"
    with open(hptx_filename, "w", encoding="utf-8") as f:
        f.write(hptx)
    print(f"✅ Tutorial HPTX generado: {hptx_filename}")

    print("🔄 Convirtiendo HPTX → JSON HIPERTEX...")
    data = hptx_to_json(hptx)

    json_filename = f"{slug}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON HIPERTEX generado: {json_filename}")


if __name__ == "__main__":
    main()

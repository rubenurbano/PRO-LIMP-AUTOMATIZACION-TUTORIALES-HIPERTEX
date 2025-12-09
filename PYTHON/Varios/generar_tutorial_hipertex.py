#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de tutoriales HIPERTEX (.hptx + .json) usando Gemini (google-genai)

Flujo:
1. Pide el título del vídeo / contenido.
2. Busca la transcripción en un .txt con el mismo nombre.
3. Construye un prompt usando las reglas de "Reglas para los tutoriales paso a paso.txt" (si existe).
4. Llama a Gemini (gemini-1.5-flash) con sistema de reintentos (manejo de 503 / overloaded).
5. Guarda la salida como .hptx.
6. Llama a parser_hipertex.py para convertir .hptx → .json HIPERTEX.

Requisitos:
- Paquete `google-genai` instalado.
- Variable de entorno con la API key de Gemini (por ejemplo: GOOGLE_API_KEY).
- `parser_hipertex.py` en el mismo directorio.
"""

import os
import sys
import time
import unicodedata
import re
import subprocess
from pathlib import Path

from google import genai
from google.genai import errors

# ==============================
# CONFIGURACIÓN
# ==============================

MODEL_NAME = "gemini-1.5-flash"  # cambiado aquí
MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 5  # multiplicador simple para backoff

client = genai.Client()  # Usará la API key de entorno (GOOGLE_API_KEY / GENAI_API_KEY)


# ==============================
# UTILIDADES
# ==============================

def normalizar_titulo(titulo: str) -> str:
    """
    Normaliza un título para usarlo como nombre de archivo.
    Convierte acentos, espacios y símbolos a un slug sencillo.
    """
    titulo = titulo.strip()
    titulo = titulo.replace(".txt", "").replace(".TXT", "")
    # Quitar acentos
    nfkd = unicodedata.normalize("NFKD", titulo)
    sin_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Solo letras, números y espacios
    solo_basico = re.sub(r"[^a-zA-Z0-9]+", " ", sin_acentos)
    # Slug con guiones
    slug = "-".join(solo_basico.lower().strip().split())
    return slug or "tutorial-hipertex"


def cargar_transcripcion(titulo: str) -> tuple[str, Path]:
    """
    A partir del título, determina el nombre del .txt y devuelve (texto, ruta).
    """
    if titulo.lower().endswith(".txt"):
        nombre_txt = titulo
    else:
        nombre_txt = f"{titulo}.txt"

    ruta_txt = Path(nombre_txt)
    if not ruta_txt.exists():
        print(f"❌ No se encontró la transcripción: {ruta_txt}")
        sys.exit(1)

    try:
        texto = ruta_txt.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # fallback best-effort
        texto = ruta_txt.read_text(encoding="latin-1")

    return texto, ruta_txt


def cargar_reglas() -> str:
    """
    Intenta cargar el archivo de reglas de tutoriales paso a paso.
    Si no existe, devuelve un texto base mínimo.
    """
    ruta_reglas = Path("Reglas para los tutoriales paso a paso.txt")
    if ruta_reglas.exists():
        try:
            return ruta_reglas.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ruta_reglas.read_text(encoding="latin-1")

    # Fallback mínimo si no está el archivo
    return (
        "REGLAS PARA EL TUTORIAL HIPERTEX:\n"
        "- Explicación clara, simple y directa.\n"
        "- Mantén la estructura con tags HIPERTEX:\n"
        "  ##itemID:000\n"
        "  ##menu-item BEGIN\n"
        "  [Texto del menú]\n"
        "  ##menu-item END\n"
        "  ##Contenido BEGIN\n"
        "  [Contenido detallado del paso]\n"
        "  ##Contenido END\n"
        "- Usa varios items con itemID consecutivos (000, 001, 002...).\n"
        "- No inventes datos técnicos: basarte solo en la transcripción.\n"
    )


def construir_prompt(titulo: str, transcripcion: str) -> str:
    """
    Construye el prompt completo que se enviará a Gemini.
    Incluye las reglas y la transcripción.
    """
    reglas = cargar_reglas()
    prompt = f"""
{reglas}

=== CONTEXTO DEL CONTENIDO ===
Título del vídeo o recurso:
{titulo}

=== TRANSCRIPCIÓN COMPLETA (EN CASTELLANO O IDIOMA ORIGINAL) ===
{transcripcion}

=== OBJETIVO ===
A partir de la transcripción, genera un TUTORIAL HIPERTEX (.hptx) siguiendo ESTRICTAMENTE estas reglas:

1. El resultado debe ser texto plano con los tags HIPERTEX, por ejemplo:
   ##itemID:000
   ##menu-item BEGIN
   [Título o descripción del paso]
   ##menu-item END
   ##Contenido BEGIN
   [Desarrollo detallado del paso]
   ##Contenido END

2. Usa itemID consecutivos empezando en 000.
3. Cada menú tiene su Contenido, pero puede haber Contenidos sin menú.
4. No escribas explicaciones adicionales fuera del formato HIPERTEX.
5. No pongas código Markdown ni comentarios, solo el contenido HIPERTEX.

=== SALIDA ESPERADA ===
Devuelve únicamente el contenido HIPERTEX listo para guardarse en un archivo .hptx.
"""
    return prompt


# ==============================
# LLAMADA A GEMINI CON RETRY
# ==============================

def llamar_gemini_con_retry(prompt: str) -> str:
    """
    Llama a Gemini con sistema de reintentos ante errores 503 / overloaded.
    """
    for intento in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            # La librería google-genai ofrece .text para concatenar partes
            return response.text
        except errors.ServerError as e:
            msg = str(e)
            code = getattr(e, "status_code", None)

            # Detectar sobrecarga / service unavailable
            if code == 503 or "overloaded" in msg.lower() or "unavailable" in msg.lower():
                if intento < MAX_RETRIES:
                    wait = BASE_BACKOFF_SECONDS * intento
                    print(f"⚠️ Gemini sobrecargado (503) intento {intento}/{MAX_RETRIES}. Esperando {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    print("❌ Gemini sigue sobrecargado después de varios intentos.")
                    raise
            else:
                # Cualquier otro ServerError no lo tocamos
                print("❌ Error de servidor de Gemini no recuperable:")
                raise
        except Exception as e:
            print("❌ Error inesperado llamando a Gemini:")
            raise

    raise RuntimeError("No se pudo obtener respuesta de Gemini tras varios reintentos.")


# ==============================
# CONVERSIÓN HPTX → JSON HIPERTEX
# ==============================

def convertir_hptx_a_json(ruta_hptx: Path) -> Path:
    """
    Llama a parser_hipertex.py para convertir un .hptx en .json HIPERTEX.
    Usa el mismo intérprete de Python que está ejecutando este script.
    """
    ruta_json = ruta_hptx.with_suffix(".json")
    cmd = [sys.executable, "parser_hipertex.py", str(ruta_hptx)]

    print("🔄 Convirtiendo HPTX → JSON HIPERTEX...")
    try:
        with ruta_json.open("w", encoding="utf-8") as f_out:
            subprocess.run(cmd, check=True, stdout=f_out)
    except FileNotFoundError:
        print("❌ No se encontró parser_hipertex.py en el directorio actual.")
        raise
    except subprocess.CalledProcessError as e:
        print("❌ Error ejecutando parser_hipertex.py:")
        raise e

    return ruta_json


# ==============================
# MAIN
# ==============================

def main() -> None:
    print("=== Generador HPTX + JSON con Gemini (google-genai) ===")

    titulo = input("Título del vídeo / contenido: ").strip()
    if not titulo:
        print("❌ No se ingresó título. Saliendo.")
        return

    slug = normalizar_titulo(titulo)
    print(f"📝 Título normalizado: {slug}")

    # Cargar transcripción
    transcripcion, ruta_txt = cargar_transcripcion(titulo)
    print(f"📄 Usando transcripción desde archivo: {ruta_txt.name}")

    # Construir prompt
    prompt = construir_prompt(titulo, transcripcion)

    # Llamar a Gemini con retry
    print(f"🧠 Generando tutorial HPTX con modelo: {MODEL_NAME} ...")
    hptx_contenido = llamar_gemini_con_retry(prompt)

    # Guardar .hptx
    ruta_hptx = Path(f"{slug}.hptx")
    ruta_hptx.write_text(hptx_contenido, encoding="utf-8")
    print(f"✅ Tutorial HPTX generado: {ruta_hptx.name}")

    # Convertir a JSON HIPERTEX
    try:
        ruta_json = convertir_hptx_a_json(ruta_hptx)
        print(f"✅ JSON HIPERTEX generado: {ruta_json.name}")
    except Exception:
        print("⚠️ No se pudo convertir a JSON HIPERTEX. Revisa parser_hipertex.py y el archivo .hptx.")
        raise


if __name__ == "__main__":
    main()

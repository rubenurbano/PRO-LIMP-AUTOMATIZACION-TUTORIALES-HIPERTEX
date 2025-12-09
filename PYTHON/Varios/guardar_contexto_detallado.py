from supabase import create_client
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
guardar_contexto_detallado.py
- Inserta entradas de bitácora técnica en public.contextos_orion (Supabase)
- Lee SUPABASE_URL y SUPABASE_KEY desde variables de entorno
- Admite argumentos por CLI para no editar el .py cada vez
"""

from supabase import create_client
from datetime import datetime, timezone
from typing import List, Optional
import argparse
import os
import sys


def require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"Falta variable de entorno {name}")
    return val


def parse_list(text: Optional[str]) -> Optional[List[str]]:
    """
    Convierte 'a; b; c' o 'a,b,c' en ['a','b','c'].
    Si viene None o cadena vacía, devuelve None.
    """
    if not text:
        return None
    sep = ";" if ";" in text else ","
    items = [x.strip() for x in text.split(sep)]
    return [x for x in items if x]


def guardar_contexto_detallado(
    titulo: str,
    errores: Optional[List[str]] = None,
    causas: Optional[List[str]] = None,
    soluciones: Optional[str] = None,
    etiquetas: Optional[List[str]] = None,
    fuente: str = "orion",
):
    url = require_env("SUPABASE_URL")
    key = require_env("SUPABASE_KEY")

    supabase = create_client(url, key)

    data = {
        "fecha": datetime.now(timezone.utc).isoformat(),
        "titulo": titulo,
        "errores": errores,
        "causas": causas,
        "soluciones": soluciones,
        "etiquetas": etiquetas or ["bitácora", "problemas"],
        "fuente": fuente,
    }

    # Limpia claves con None para no forzar nulls innecesarios
    payload = {k: v for k, v in data.items() if v is not None}

    try:
        supabase.table("contextos_orion").insert(payload).execute()
        print("Contexto técnico guardado correctamente.")
    except Exception as e:
        print("Error al guardar el contexto:", e)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Guardar una entrada en public.contextos_orion (Supabase).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "-t", "--titulo", required=True, help="Título breve del contexto."
    )
    p.add_argument(
        "-e", "--errores",
        help="Lista de errores separada por ';' o ','. Ej.: \"timeout; loading infinito\"",
    )
    p.add_argument(
        "-c", "--causas",
        help="Lista de causas separada por ';' o ','. Ej.: \"caché; CORS\"",
    )
    p.add_argument(
        "-s", "--soluciones",
        help="Descripción de la solución aplicada (texto libre).",
    )
    p.add_argument(
        "-x", "--etiquetas",
        help="Lista de etiquetas separada por ';' o ','. Ej.: \"supabase; python; debug\"",
    )
    p.add_argument(
        "-f", "--fuente",
        default="orion",
        help="Origen o herramienta (vscode, colab, gemini, etc.).",
    )
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    guardar_contexto_detallado(
        titulo=args.titulo,
        errores=parse_list(args.errores),
        causas=parse_list(args.causas),
        soluciones=args.soluciones,
        etiquetas=parse_list(args.etiquetas),
        fuente=args.fuente,
    )


if __name__ == "__main__":
    main()

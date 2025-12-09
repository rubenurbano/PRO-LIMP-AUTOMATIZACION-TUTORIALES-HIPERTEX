import asyncio
import csv
import os
import re
from urllib.parse import urlparse

import requests
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# URL PUBLICADA COMO CSV de tu Google Sheet
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTy7ua0I8u3h4alZS9tbogYrtt6Cu5Pv7q2q_g3kuSuv0Yg4ca6uN5ebU8t6MewL5ELXzeQNXj13xtl/pub?gid=0&single=true&output=csv"
)

# Carpeta donde se guardarán los archivos de salida
OUTPUT_DIR = "notebooklm_crawls"


def load_rows_from_sheet(csv_url: str):
    """
    Descarga el CSV público de Google Sheets y devuelve
    una lista de (url, base_filename, mode).
    """
    print(f"Descargando URLs desde Google Sheets...\n{csv_url}\n")
    resp = requests.get(csv_url, timeout=30)
    resp.raise_for_status()

    rows: list[tuple[str, str, str]] = []
    reader = csv.reader(resp.text.splitlines())

    first_row = True
    for row in reader:
        if not row:
            continue

        url_cell = row[0].strip() if len(row) > 0 else ""
        name_cell = row[1].strip() if len(row) > 1 else ""
        mode_cell = row[2].strip() if len(row) > 2 else ""

        # Saltar la cabecera (primera fila) si no empieza por http
        if first_row and not url_cell.startswith(("http://", "https://")):
            first_row = False
            continue
        first_row = False

        if not url_cell.startswith(("http://", "https://")):
            continue

        if not name_cell:
            name_cell = safe_basename_from_url(url_cell)

        if not mode_cell:
            mode_cell = "md"

        rows.append((url_cell, name_cell, mode_cell.lower()))

    print(f"Encontradas {len(rows)} filas válidas (URL + nombre + modo).\n")
    return rows


def safe_basename_from_url(url: str) -> str:
    """
    Convierte una URL en un nombre base de archivo válido (sin extensión).
    """
    parsed = urlparse(url)
    base = (parsed.netloc + parsed.path).strip("/")
    if not base:
        base = "page"
    base = re.sub(r'[<>:"/\\|?*]+', "_", base)
    return base


def ensure_extension(name: str, ext: str) -> str:
    """
    Asegura que el nombre de archivo termine en la extensión dada.
    """
    if not name.lower().endswith(ext):
        name = name + ext
    return name


def build_links_markdown(result) -> str | None:
    """
    Construye un listado de enlaces en markdown a partir de result.links.
    """
    links = getattr(result, "links", None)
    if not links:
        return None

    lines = ["# Enlaces extraídos", ""]
    # links suele ser un dict url -> texto o similar
    if isinstance(links, dict):
        for url, text in links.items():
            text_str = str(text).strip() if text else url
            lines.append(f"- [{text_str}]({url})")
    elif isinstance(links, list):
        for item in links:
            url = getattr(item, "url", None) or str(item)
            text = getattr(item, "text", "") or url
            lines.append(f"- [{text}]({url})")
    else:
        # Formato raro, lo volcamos tal cual
        lines.append(str(links))

    lines.append("")
    return "\n".join(lines)


async def crawl_urls(rows: list[tuple[str, str, str]]) -> None:
    """
    Usa Crawl4AI para procesar cada fila según el modo indicado
    y guardar el resultado en archivos dentro de OUTPUT_DIR.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    browser_config = BrowserConfig(
        headless=True,
        java_script_enabled=True,
    )

    run_config = CrawlerRunConfig(
        wait_until="networkidle",
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        total = len(rows)
        for idx, (url, base_name, mode) in enumerate(rows, start=1):
            print(f"[{idx}/{total}] Crawling: {url}  (modo: {mode})")
            result = await crawler.arun(url=url, config=run_config)

            if not getattr(result, "success", False):
                print(
                    f"  ✗ Error: {getattr(result, 'error_message', 'Error desconocido')}\n"
                )
                continue

            # --- MODO md / md-fit ---
            if mode in ("md", "md-fit"):
                md = None
                md_obj = getattr(result, "markdown", None)

                if isinstance(md_obj, str):
                    md = md_obj
                elif md_obj is not None:
                    if mode == "md-fit":
                        md = getattr(md_obj, "fit_markdown", None) or getattr(
                            md_obj, "raw_markdown", None
                        )
                    else:  # md
                        md = getattr(md_obj, "raw_markdown", None) or getattr(
                            md_obj, "fit_markdown", None
                        )

                if not md:
                    print("  ✗ No se obtuvo Markdown. Saltando.\n")
                    continue

                filename = ensure_extension(base_name, ".md")
                out_path = os.path.join(OUTPUT_DIR, filename)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(md)
                print(f"  ✓ Guardado en: {out_path}\n")
                continue

            # --- MODO links ---
            if mode == "links":
                links_md = build_links_markdown(result)
                if not links_md:
                    print("  ✗ No se encontraron enlaces. Saltando.\n")
                    continue

                filename = ensure_extension(base_name, ".links.md")
                out_path = os.path.join(OUTPUT_DIR, filename)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(links_md)
                print(f"  ✓ Enlaces guardados en: {out_path}\n")
                continue

            # --- Modos no soportados aún ---
            print(
                f"  ✗ Modo '{mode}' aún no soportado por el script. Fila saltada.\n"
            )


def main() -> None:
    rows = load_rows_from_sheet(GOOGLE_SHEET_CSV_URL)
    if not rows:
        print(
            "No hay filas válidas en la hoja. Revisa el CSV (URL, nombre_salida, modos)."
        )
        return

    asyncio.run(crawl_urls(rows))
    print(f"Terminado. Archivos listos en: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

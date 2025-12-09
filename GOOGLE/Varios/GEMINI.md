# GEMINI.md - Project Overview: HIPERTEX

## Project Overview

This project, named **HIPERTEX**, is a lightweight content management and viewing system designed for creating and rendering tutorials. The core idea is to write tutorials in a simple text-based format (`.hptx`, `.txt`, or even `.docx`) using specific tags, and then parse these files into a structured JSON format. This JSON can then be loaded by a local HTML viewer for an interactive experience with a menu and content sections.

The main technologies used are:

*   **Python:** For the core parsing logic (`parser_hipertex.py`), catalog generation (`build_catalog.py`), and validation utilities.
*   **PowerShell:** For orchestrating the conversion process (`HIPERTEX_SETUP.ps1`).
*   **HTML & JavaScript:** For the interactive front-end viewer (`visor_hipertex.html`) that consumes the generated JSON.

## Building and Running

The project does not have a traditional build process. Instead, it operates through a series of scripts.

### 1. Converting a Tutorial (`.hptx` to `.json`)

The main workflow is to convert a source tutorial file into its JSON representation.

1.  Open a PowerShell terminal in this directory.
2.  Run the main setup script:
    ```powershell
    .\HIPERTEX_SETUP.ps1
    ```
3.  The script will prompt you to enter the name of the source file (e.g., `ejemplo HPTX.hptx`).
4.  It will then execute the Python parser and generate a corresponding `.json` file (e.g., `ejemplo HPTX.json`).

### 2. Viewing a Tutorial

Once the JSON file is generated, you can view it using one of the provided HTML viewers.

1.  Open `visor_hipertex.html` or `cargador universal HPTX.html` in your web browser.
2.  Use the "Seleccionar archivo" button to load the `.json` file you just created.

### 3. Building the Project Catalog

To generate a central `catalog.json` file that indexes all the `.hptx` tutorials in the directory:

```powershell
py build_catalog.py --root . --out catalog.json
```

### 4. Validating JSON Output

To ensure the generated JSON is well-formed, you can use the verification scripts:

```powershell
# First, normalize the JSON
py normalizar_hipertex.py "Your_Tutorial_File.json"

# Then, verify the normalized file
py verificador_hipertex.py "Your_Tutorial_File.normalized.json"
```

## Development Conventions

*   **Content Format (`.hptx`):** Tutorials are structured using specific tags:
    *   `##HIPERTEX-META BEGIN` / `##HIPERTEX-META END`: Defines metadata for the tutorial (title, tags, creation date).
    *   `##itemID:xxx`: Defines a unique ID for a content block.
    *   `##menu-item BEGIN` / `##menu-item END`: Defines the title of an item that will appear in the menu.
    *   `##Contenido BEGIN` / `##Contenido END`: Defines the main content for an item.
*   **Dependencies:** The Python scripts have minimal dependencies. `python-docx` and `charset-normalizer` are required for `parser_hipertex.py`.
*   **File Naming:** The scripts rely on specific file naming conventions (e.g., the parser generates `*_parsed.json` which is then renamed).
*   **Encoding:** The project consistently uses UTF-8 encoding for text and JSON files.

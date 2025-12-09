
import os
import shutil

# Configuración
ROOT_DIR = "C:/Users/rubenurbano/HIPERTEX"
CATEGORIES = {
    "FASTAPI": ["FASTAPI", "API"],
    "PYTHON": ["PYTHON", "PY", "PIP", "CONDA", "JUPYTER"],
    "DOCKER": ["DOCKER", "CONTAINER"],
    "MAKE": ["MAKE", "MAKE.COM", "INTEGRATION", "WEBHOOK", "ROUTER", "FILTER", "JSON"],
    "APPSHEET": ["APPSHEET"],
    "GOOGLE": ["GOOGLE", "GEMINI", "APPS SCRIPT", "COLAB", "SHEETS", "GMAIL", "FIREBASE", "ANDROID"],
    "EXCEL": ["EXCEL", "XLSX"],
    "CHATGPT": ["CHATGPT", "GPT", "OPENAI"],
    "CLAUDE": ["CLAUDE", "ANTHROPIC"],
    "PERPLEXITY": ["PERPLEXITY"],
    "TELEGRAM": ["TELEGRAM", "BOT"],
    "LINKEDIN": ["LINKEDIN"],
    "MANYCHAT": ["MANYCHAT"],
    "STRIPE": ["STRIPE"],
    "NOTEBOOKLM": ["NOTEBOOKLM"],
    "SUPABASE": ["SUPABASE"],
    "FLET": ["FLET"],
    "REACT": ["REACT", "TSX", "VITE"],
    "N8N": ["N8N"],
    "PIANO": ["PIANO", "ACORDES", "MUSIC"],
    "GIT": ["GIT", "GITHUB"],
}

# Carpetas a ignorar
IGNORE_DIRS = [".git", "venv", "__pycache__", "node_modules", ".gemini", ".history", "PRO-LIMP-AUTOMATIZACION-TUTORIALES-HIPERTEX"]
IGNORE_FILES = ["organizar_hipertex.py", "HIPERTEX_SETUP.ps1", "build_catalog.py", "visor_hipertex.html", "catalog.json"]

def get_category(filename):
    name_upper = filename.upper()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in name_upper:
                return category
    return "OTROS"

def get_type_folder(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".hptx":
        return "HPTX"
    elif ext == ".json":
        return "JSON"
    else:
        return "Varios"

def organize():
    print(f"Organizando archivos en {ROOT_DIR}...")
    
    # Crear lista de movimientos primero para no iterar sobre lo que estamos moviendo
    moves = []
    
    # Listar solo archivos en la raíz (no recursivo inicialmente para evitar mover cosas dentro de subcarpetas ya creadas)
    for filename in os.listdir(ROOT_DIR):
        file_path = os.path.join(ROOT_DIR, filename)
        
        # Ignorar directorios y archivos específicos
        if os.path.isdir(file_path):
            continue
        if filename in IGNORE_FILES:
            continue
            
        category = get_category(filename)
        type_folder = get_type_folder(filename)
        
        dest_dir = os.path.join(ROOT_DIR, category, type_folder)
        dest_path = os.path.join(dest_dir, filename)
        
        moves.append((file_path, dest_dir, dest_path, category, type_folder))

    # Ejecutar movimientos
    count = 0
    for file_path, dest_dir, dest_path, category, type_folder in moves:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        try:
            shutil.move(file_path, dest_path)
            print(f"MOVIDO: {os.path.basename(file_path)} -> {category}/{type_folder}")
            count += 1
        except Exception as e:
            print(f"ERROR moviendo {file_path}: {e}")

    print(f"\nFinalizado. {count} archivos organizados.")

    enforce_subfolders()

def enforce_subfolders():
    print("\nVerificando subcarpetas (HPTX, JSON, Varios)...")
    subfolders = ["HPTX", "JSON", "Varios"]
    
    for item in os.listdir(ROOT_DIR):
        item_path = os.path.join(ROOT_DIR, item)
        
        # Procesar solo directorios que no estén en la lista de ignorados
        if os.path.isdir(item_path) and item not in IGNORE_DIRS:
            for sub in subfolders:
                sub_path = os.path.join(item_path, sub)
                if not os.path.exists(sub_path):
                    os.makedirs(sub_path)
                    print(f"CREADO: {item}/{sub}")

if __name__ == "__main__":
    organize()

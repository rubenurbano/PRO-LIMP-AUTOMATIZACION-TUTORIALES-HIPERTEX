# verificar_mcp_lanzado.py
# -------------------------------------------------------
# Uso recomendado:
# 1) Asegúrate de que NO tienes abierto manualmente mcp_server.py.
# 2) Abre ChatGPT Desktop y espera unos segundos.
# 3) Ejecuta:  python verificar_mcp_lanzado.py
# 4) Si ChatGPT lanzó el servidor MCP, verás un mensaje ✅.
# -------------------------------------------------------

import sys

try:
    import psutil
except ImportError:
    print("❌ La librería 'psutil' no está instalada.")
    print("Instálala con:\n    pip install psutil")
    sys.exit(1)

TARGET = "mcp_server.py"

def main() -> None:
    found = False
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = (proc.info.get("name") or "").lower()
            cmdline = proc.info.get("cmdline") or []
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        if "python" in name and any(TARGET.lower() in (arg or "").lower() for arg in cmdline):
            if not found:
                print("✅ Proceso MCP encontrado:")
                found = True
            print(f"  PID {proc.pid} → {' '.join(cmdline)}")

    if not found:
        print("⚠️ No se encontró ningún proceso Python ejecutando", TARGET)
        print("   - Si esperabas que ChatGPT lo lanzara automáticamente, aún no lo está haciendo.")
        print("   - Puedes seguir lanzándolo manualmente con:")
        print("       python C:\\Users\\rubenurbano\\HIPERTEX\\mcp_server.py")

if __name__ == "__main__":
    main()


# normalizar_hipertex.py
import sys, json
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".normalized.json")

data = json.loads(src.read_text(encoding="utf-8"))
items = data["items"] if isinstance(data, dict) and isinstance(data.get("items"), list) else data
if not isinstance(items, list):
    raise SystemExit("El JSON no contiene lista de items ni clave 'items' válida.")

dst.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✅ Guardado: {dst}")

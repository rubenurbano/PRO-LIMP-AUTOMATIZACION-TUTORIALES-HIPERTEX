# verificador_hipertex.py
import sys, json, re
from pathlib import Path

def load_items(p: Path):
    data = json.loads(p.read_text(encoding="utf-8"))
    # Acepta lista o {"items": [...]}
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    raise ValueError("El JSON debe ser una lista o un objeto con clave 'items' que sea lista.")

def validate(items):
    ok = True
    menu_items = []

    for it in items:
        menu_val = it.get("menu-item") or it.get("menu_item") or ""
        if isinstance(menu_val, str) and menu_val.strip():
            menu_items.append(it)

    # 1) Numeración de menús secuenciales
    for idx, it in enumerate(menu_items, start=1):
        expected = f"{idx:03d}"
        actual = str(it.get("itemID") or it.get("id") or "").strip()
        if actual != expected:
            print(f"⚠️ itemID esperado {expected} pero encontrado '{actual}' en: {menu_val!r}")
            ok = False

    # 2) Contenido obligatorio
    for it in items:
        cont = it.get("contenido") or it.get("Contenido") or ""
        if not isinstance(cont, str) or not cont.strip():
            print(f"⚠️ Falta contenido en itemID: {it.get('itemID')}")
            ok = False

    # 3) Formato del itemID
    for it in items:
        if "itemID" in it and it["itemID"]:
            if not re.fullmatch(r"\d{3}", str(it["itemID"])):
                print(f"⚠️ itemID inválido '{it['itemID']}' (usa formato 000, 001, 002...)")
                ok = False

    return ok

def main():
    if len(sys.argv) < 2:
        print("Uso: py verificador_hipertex.py <archivo.json>")
        sys.exit(2)
    p = Path(sys.argv[1])
    try:
        items = load_items(p)
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)

    if validate(items):
        print(f"✅ Archivo HIPERTEX válido: {len(items)} items revisados correctamente.")
    else:
        print("⚠️ Se detectaron advertencias. Revisa los avisos arriba.")

if __name__ == "__main__":
    main()

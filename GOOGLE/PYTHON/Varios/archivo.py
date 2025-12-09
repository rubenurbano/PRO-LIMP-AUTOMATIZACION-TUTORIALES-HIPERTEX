from toon import encode, decode  # <--- IMPORT CORRECTO

data = {
    "users": [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
    ]
}

# Python → TOON
toon_text = encode(data)
print("=== TOON ===")
print(toon_text)

# TOON → Python
back = decode(toon_text)
print("=== PYTHON ===")
print(back)

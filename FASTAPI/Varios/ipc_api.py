from fastapi import FastAPI
import requests
import re

app = FastAPI()

def obtener_ipc():
    url = "https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176802&menu=ultiDatos&idp=1254735976607"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    match = re.search(r'IPC\s+sitúa\s+su\s+variación\s+anual\s+en\s+el\s+([\d,]+)%', response.text)
    if match:
        return float(match.group(1).replace(',', '.'))  # 👈 Convierte a float
    return None

@app.get("/ipc")
def leer_ipc():
    valor = obtener_ipc()
    return {"ipc": valor}

import requests
import re

def obtener_ipc():
    url = "https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176802&menu=ultiDatos&idp=1254735976607"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    match = re.search(r'IPC\s+sitúa\s+su\s+variación\s+anual\s+en\s+el\s+([\d,]+)%', response.text)
    if match:
        return float(match.group(1).replace(',', '.'))
    else:
        return None

if __name__ == "__main__":
    valor_ipc = obtener_ipc()
    print("Valor IPC:", valor_ipc)

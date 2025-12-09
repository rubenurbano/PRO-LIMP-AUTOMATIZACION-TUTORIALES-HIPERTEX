from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, re

app = FastAPI()

# Orígenes permitidos (ajusta según tu front)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # o ["*"] si quieres abrirlo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def obtener_ipc():
    url = "https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176802&menu=ultiDatos&idp=1254735976607"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    r.encoding = "utf-8"
    m = re.search(r'IPC\s+sitúa\s+su\s+variación\s+anual\s+en\s+el\s+([\d,]+)%', r.text)
    return float(m.group(1).replace(',', '.')) if m else None

@app.get("/ipc")
def leer_ipc():
    return {"ipc": obtener_ipc()}


#En tu front (React/Vite, etc.) llama a tu API:
#const resp = await fetch("http://127.0.0.1:8000/ipc");
#const data = await resp.json();
#console.log(data.ipc); // 3.1 (float)
#Evita esto

#❌ fetch('https://www.ine.es/...') desde el navegador → CORS del INE.

#✅ Siempre fetch('http://127.0.0.1:8000/ipc') (o la IP/puerto donde corre tu FastAPI/NSSM).

#Si luego lo expones en tu red o internet, añade el origen real (dominio o IP:puerto) en origins y listo.
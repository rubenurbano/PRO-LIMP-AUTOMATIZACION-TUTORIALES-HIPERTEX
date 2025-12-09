Readme - Plantilla FASTAPI (con almacenamiento JSON)

Guardá este archivo como main.py en una carpeta nueva.(Plantilla FASTAPI —(con almacenamiento JSON).txt)

En la terminal:

uvicorn main:app --reload


Abrí en tu navegador:

http://127.0.0.1:8000 → mensaje de bienvenida

http://127.0.0.1:8000/docs → interfaz Swagger lista para usar

Qué hace:

Crea automáticamente un archivo data.json al guardar el primer item.

Todos los datos que agregues o borres se guardan y persisten entre sesiones.

El endpoint /info te muestra la ruta exacta del archivo JSON que usa.
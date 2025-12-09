from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

items_db = [
    {"item_id": 1, "name": "Laptop", "description": "Potente laptop para trabajo", "price": 1200.0, "tax": 120.0},
    {"item_id": 2, "name": "Mouse", "description": "Mouse ergonómico", "price": 25.0, "tax": 2.5},
    {"item_id": 3, "name": "Teclado", "description": "Teclado mecánico RGB", "price": 80.0, "tax": 8.0},
    {"item_id": 4, "name": "Monitor", "description": "Monitor 4K de 27 pulgadas", "price": 350.0, "tax": 35.0},
]
next_item_id = 5

@app.get("/")
async def read_root():
    return {"message": "¡Bienvenido a mi API de Artículos!"}

@app.get("/items/", response_model=List[Item])
async def read_items(skip: int = 0, limit: int = 10):
    return items_db[skip : skip + limit]

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    for item in items_db:
        if item["item_id"] == item_id:
            return item
    return {"message": "Item no encontrado"}

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    global next_item_id
    new_item = item.dict()
    new_item["item_id"] = next_item_id
    items_db.append(new_item)
    next_item_id += 1
    return new_item

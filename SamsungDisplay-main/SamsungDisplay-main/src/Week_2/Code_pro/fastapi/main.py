# main.py
from fastapi import FastAPI

app = FastAPI(title="OrderBean API")

@app.get("/")
def root():
    return {"message": "OrderBean backend running !"}

@app.get("/menu/{item_id}")
def get_menu(item_id: int):
    return {"item_id": item_id, "name": "Americano", "price": 4500}
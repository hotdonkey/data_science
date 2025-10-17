
import os
import random
from typing import Union
from fastapi import FastAPI, HTTPException, Request, Response, status, Header, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import threading
import requests
import time
import yaml
import subprocess
import wget


# 1. Создаем объект класса для инициалицации сервера
app = FastAPI()

# 2. Имитация бд через словарь
db = dict()

# 3. Дата-классы
class Item(BaseModel):
    name: str
    description: str = None
    price: float

class ItemConfidential(BaseModel):
    name: str
    description: str = None


# 4. Прокинем методы в ассинхронном режиме
# все текстовки на английском изза utf-8

# Нулевой эндпоинт
@app.get("/")
async def read_root():
    return {"message":"Everything seems OK!! Server is running",
            "/json_data":"Endpoint with JSON responce",
            "/error":"Randomly generated error code"}

# GET /items - вывод всех айтемов
@app.get("/items", response_model=list[Item])
async def list_items():
    return list(db.values())

# POST /items - cоздание единичного айтема
@app.post("/items", status_code=status.HTTP_201_CREATED, response_model=ItemConfidential)
async def create_item(item: Item):
    item_id = len(db) + 1
    db[item_id] = item
    return item 

# GET /items/{item_id} - тащим айтем по айдишнику
@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, q: Union[str, None] = None):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    return db[item_id]

# PUT /items/{item_id} - обновляем айтем 
@app.put("/items/{item_id}", response_model=Item)
async def update_item_put(item_id: int, item: Item):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    db[item_id] = item
    return item

# PATCH /items/{item_id} - обновляем айтем 
@app.patch("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    db[item_id] = item
    return item

# DELETE /items/{item_id} - удаляем айтем
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    del db[item_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Эндпоинт ответа json файлом
@app.get("/json_data", response_class=JSONResponse)
async def get_json_data():
    return {"message": "This is valid JSON", "data": [1, 2, 3], "success": True}


# Генерируем рандомный код ошибки сервера
# Описание: Рандомно сгенерированный код: status_code
# так как я решил не фиксировать сид а брать из всего диапазона,
# то формируем обобзенный ответ:
# все что выше 500-сервер, все что ниже клиент
status_code = random.randint(400, 526)

if 500 <= status_code <= 599:
    error_detail = f"Internal server proplem ({status_code})."
else:
    error_detail = f"Client side problem {status_code} - check your query."

# Эндпоинт /error, возвращающий HTTP-ошибку
@app.get("/error")
async def trigger_error():
    raise HTTPException(status_code=401, detail=error_detail)

if __name__ == "__main__":
    # Берем api_key из конфигурационного файла
    with open("config.yaml", "r", encoding="utf-8") as f:
        XTUNNEL_API_KEY = yaml.safe_load(f)["KEY"]

    # Создадим папку для xtunnel
    os.makedirs("./xtunnel", exist_ok=True)

    # Для запуска из консоли
    # platform = input("Choose your platform (osx, linux, win), note linux/win on x64 not ARM")

    # Для запуска из юпитера так как нет доступа к вводу
    platform = "osx"

    base_url = "https://github.com/xtunnel-dev/xtunnel-binaries/raw/refs/heads/main/1.0.20/"

    if platform == "osx":
        binary = base_url + "xtunnel.osx-arm64.1.0.20.zip"
    elif platform == "linux":
        binary = base_url + "xtunnel.linux-x64.1.0.20.zip"
    elif platform == "win":
        binary = base_url + "xtunnel.win-x64.1.0.20.zip"
    else:
        raise ValueError("Unsupported platform")

    # Скачиваем через subprocess(так как запускаем из py-файла и bash скрипты дадут ошибку)
    subprocess.run([
        "curl", "-L", "-o", "./xtunnel/xt.zip",
        binary
    ])

    # Распаковываем
    subprocess.run(["unzip", "-o", "./xtunnel/xt.zip", "-d", "./xtunnel/"])

    # Даём права на выполнение (macOS/Linux)
    os.chmod("./xtunnel/xtunnel", 0o755)

    # Регистрируем
    subprocess.run(["./xtunnel/xtunnel", "register", XTUNNEL_API_KEY])
    xtunnel_proc = subprocess.Popen(["./xtunnel/xtunnel", "http", "8090"])

    # Запускаем сервер и туннель
    uvicorn_proc = subprocess.Popen(["uvicorn", "main:app", "--port", "8090", "--host", "0.0.0.0"])
    time.sleep(5)
    xtunnel_proc = subprocess.Popen(["./xtunnel/xtunnel", "http", "8090"])

    # Ждём завершения
    try:
        xtunnel_proc.wait()
    except KeyboardInterrupt:
        uvicorn_proc.terminate()
        xtunnel_proc.terminate()

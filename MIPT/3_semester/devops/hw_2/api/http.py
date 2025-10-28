
from fastapi import FastAPI
from application.services import old_system_http, new_system, should_use_new_system
from infrastructure.repository import init_db 

app = FastAPI()

# Сформируем базовый эндпоинт
@app.get("/")
def root():
    return {"message": "Strangler Fig is running"}

# Вызываем init_db при старте приложения, выводя его из main()
@app.on_event("startup")
def startup_event():
    init_db()

# Старая система
@app.get("/v1/info")
def legacy_info():
    return {"name": "Ivan Ivanov", "email": "ivan@example.com"}

# Новая система
@app.get("/v2/info")
def strangler_fig_endpoint(user_id=1):
    if should_use_new_system(traffic_percentage=50):
        user = new_system(user_id)
    else:
        user = old_system_http()
    return {"name": user.name, "email": user.email}

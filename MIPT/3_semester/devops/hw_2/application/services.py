
import random
import httpx
from domain.models import User
from infrastructure.repository import get_user_by_id

# URL старой системы 
LEGACY_URL = "http://127.0.0.1:8000/v1/info"

def old_system_http():
    """Выполняет реальный HTTP-запрос к старой системе."""
    response = httpx.get(LEGACY_URL)
    data = response.json()
    return User(name=data["name"], email=data["email"])

def new_system(user_id):
    return get_user_by_id(user_id)

def should_use_new_system(force_new=False, traffic_percentage=50):
    if force_new:
        return True
    return random.randint(0, 99) < traffic_percentage

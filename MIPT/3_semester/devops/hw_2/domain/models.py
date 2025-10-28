
from dataclasses import dataclass

# Создаем модель данных для пользователя без зависимостей от инфраструктуры
@dataclass
class User:
    name: str
    email: str

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Определяем абсолютный путь к текущему файлу
basedir = os.path.abspath(os.path.dirname(__file__))

# Создаем экземпляр Flask приложения
app = Flask(__name__)

# Устанавливаем секретный ключ приложения
app.config["SECRET_KEY"] = "you-will-never-guess"

# Устанавливаем URI базы данных. Если переменная окружения `DATABASE_URL` не установлена,
# используется SQLite база данных в файле `app.db` в текущем каталоге.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or \
    "sqlite:///" + os.path.join(basedir, "app.db")

# Отключаем отслеживание изменений в объектах ORM для улучшения производительности
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Создаем экземпляр SQLAlchemy, который связывается с Flask приложением
db = SQLAlchemy(app)

# Создаем экземпляр Flask-Migrate, который связывается с Flask приложением и базой данных
migrate = Migrate(app, db)

# Импортируем маршруты и модели данных приложения
from app import routes, models
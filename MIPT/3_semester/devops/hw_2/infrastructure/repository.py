
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from domain.models import User

# Доступ к данным через SQLAlchemy
engine = create_engine("sqlite:///./app.db", echo=False)
SessionLocal = sessionmaker(bind=engine)

# Старая ЬД
OLD_DB = [{"name": "Ivan Ivanov", "email": "ivan@example.com"}]

# Выносим все все взаииодействие с БД отдельно
def init_db():
    with SessionLocal() as session:
        # Немного подредактируем запрос по созданию и вставке что бы не допускать полные дубли
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                UNIQUE(name, email)
            );
        """))

        # Выполняем вставку
        session.execute(
            text("INSERT OR IGNORE INTO users (name, email) VALUES (:name, :email)"),
            {"name": "Ivan Ivanov", "email": "ivan@example.com"}
        )
        # Тут уже опустим проверку
        session.commit()



def get_user_by_id(user_id):
    with SessionLocal() as session:
        result = session.execute(
            text("SELECT name, email FROM users WHERE id = :id"),
            {"id": user_id}
        ).fetchone()
        if result:
            return User(name=result.name, email=result.email)
        raise ValueError("User not found")

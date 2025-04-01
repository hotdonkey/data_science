import logging
import requests
import psycopg2
from psycopg2 import sql
from pydantic_settings import BaseSettings
from pydantic import SecretStr
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
from datetime import datetime

class Settings(BaseSettings):
    """Настройки конфигурации для бота и БД."""
    oath_token: SecretStr
    folder_id: SecretStr
    bot_token: SecretStr
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: SecretStr
    ya_disk_token: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

# Загружаем настройки
config = Settings()

logger = logging.getLogger(__name__)

# Настройка подключения к БД
def get_db_connection():
    return psycopg2.connect(
        host=config.db_host,
        port=config.db_port,
        database=config.db_name,
        user=config.db_user,
        password=config.db_password.get_secret_value()
    )

# Создание таблицы при первом запуске
def init_db():
    conn = None  # Инициализация переменной
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                action_time TIMESTAMP NOT NULL,
                action_text TEXT NOT NULL
            )
        """)
        conn.commit()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

# Инициализируем БД при старте
init_db()

# Функция для записи действий в БД
def log_user_action(user_id, action):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL("INSERT INTO user_actions (user_id, action_time, action_text) VALUES (%s, %s, %s)"),
            (user_id, datetime.now(), action)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
            
# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Получаем токен
def get_iam_token():
    """Получаем IAM токен для API Yandex."""
    oath_token = config.oath_token.get_secret_value()
    response = requests.post(
        'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        json={'yandexPassportOauthToken': oath_token}
    )
    response.raise_for_status()
    return response.json()['iamToken']


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /start."""
    user_id = update.message.from_user.id  # Получаем ID пользователя
    # Логируем действие пользователя
    log_user_action(user_id, "Запустил команду /start")
    await update.message.reply_html(
        rf"Hi {update.message.from_user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
    
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /help."""
    user_id = update.message.from_user.id  # Получаем ID пользователя
    log_user_action(user_id, "Запросил помощь")  # Логируем действие
    await update.message.reply_text("Help!")


async def process_message(update: Update, context: CallbackContext) -> None:
    """Обрабатывает текстовые сообщения."""
    user_id = update.message.from_user.id  # Получаем ID пользователя
    user_text = update.message.text
    log_user_action(user_id, f"Задал вопрос: {user_text}")  # Логируем действие

    # Получаем IAM токен
    iam_token = get_iam_token()
    folder_id = config.folder_id.get_secret_value()

    # Собираем запрос для API
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt",
        "completionOptions": {"temperature": 0.3, "maxTokens": 1000},
        "messages": [{"role": "user", "text": user_text}],
    }

    URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    response = requests.post(
        URL,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {iam_token}"
        },
        json=data,
    ).json()

    answer = response.get('result', {}).get('alternatives', [{}])[
        0].get('message', {}).get('text', "No answer found.")
    await update.message.reply_text(answer)


def main() -> None:
    """Запускает бота."""
    bot_token = config.bot_token.get_secret_value()
    application = Application.builder().token(bot_token).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Обработка текстовых сообщений
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, process_message))

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
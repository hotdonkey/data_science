import logging
import requests
import csv  # Импортируем библиотеку для работы с CSV
from pydantic_settings import BaseSettings
from pydantic import SecretStr
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
from datetime import datetime  # Импортируем для получения текущего времени


class Settings(BaseSettings):
    """Настройки конфигурации для бота."""
    oath_token: SecretStr
    folder_id: SecretStr
    bot_token: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


# Загружаем настройки
config = Settings()

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def get_iam_token():
    """Получаем IAM токен для API Yandex."""
    oath_token = config.oath_token.get_secret_value()
    response = requests.post(
        'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        json={'yandexPassportOauthToken': oath_token}
    )
    response.raise_for_status()
    return response.json()['iamToken']

# Функция для записи действий пользователей в CSV файл


def log_user_action(user_id, action):
    with open('user_actions.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            [user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action])


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

import pandas as pd
import logging
import yadisk
from pydantic_settings import BaseSettings
from pydantic import SecretStr
import psycopg2
from psycopg2 import sql


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

# Загружаем настройки
config = Settings()

# Настройка подключения к БД
def get_db_connection():
    return psycopg2.connect(
        host=config.db_host,
        port=config.db_port,
        database=config.db_name,
        user=config.db_user,
        password=config.db_password.get_secret_value()
    )
    
logger = logging.getLogger(__name__)

def export_to_excel(filename: str = "user_actions.xlsx"):
    """Экспортирует данные из таблицы user_actions в Excel"""
    try:
        # Подключаемся к базе данных
        conn = get_db_connection()
        
        # Выполняем запрос и получаем данные
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user_actions")
            rows = cursor.fetchall()
            
            # Получаем названия колонок
            column_names = [desc[0] for desc in cursor.description]
            
            # Создаем DataFrame
            df = pd.DataFrame(rows, columns=column_names)
            
            # Сохраняем в Excel
            df.to_excel(filename, index=False)
            logger.info(f"Данные успешно экспортированы в {filename}")

    except Exception as e:
        logger.error(f"Ошибка при экспорте данных: {e}")
    finally:
        if conn:
            conn.close()
            
            
yadisk_token = config.ya_disk_token.get_secret_value()

def transfer_to_yadick(local_file_path, disk_file_path):
    y = yadisk.YaDisk(token = yadisk_token)
    # Проверьте, подключен ли диск
    if y.check_token():
        print("Токен действителен, можно приступать к работе с файлами на Яндекс Диске.")
    else:
        print("Токен недействителен, попробуйте получить его заново.")
    
    try:
        y.upload(local_file_path, disk_file_path)
        print (f"Файл {local_file_path} успешно загружен на Яндекс Диск.")
    except Exception as e:
        print(f"He удалось загрузить файл: {e}")
        y.remove("/dashboard_data/user_actions.xlsx")
        y.upload("user_actions.xlsx", "/dashboard_data/user_actions.xlsx")

if __name__ == "__main__":

    # Выполняем экспорт
    export_to_excel()
    transfer_to_yadick("user_actions.xlsx", "/dashboard_data/user_actions.xlsx")
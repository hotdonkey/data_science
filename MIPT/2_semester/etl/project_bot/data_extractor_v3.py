from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import logging
import yadisk
import os
import traceback
from pydantic_settings import BaseSettings
from pydantic import SecretStr
import psycopg2
from psycopg2 import sql

class Settings(BaseSettings):
    """ Настройки конфигурации для бота и БД. """
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

# Настройка подключения к БД
def get_db_connection():
    try:
        return psycopg2.connect(
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            user=config.db_user,
            password=config.db_password.get_secret_value()
        )
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}\n{traceback.format_exc()}")
        raise

logger = logging.getLogger(__name__)

def export_to_excel(filename: str = "user_actions.xlsx"):
    """ Экспортирует данные из таблицы user_actions в Excel """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user_actions")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=column_names)
            df.to_excel(filename, index=False)
            logger.info(f"Данные успешно экспортированы в {filename}")
    except Exception as e:
        logger.error(f"Ошибка при экспорте данных: {e}\n{traceback.format_exc()}")
    finally:
        if conn:
            conn.close()

def transfer_to_yadisk(local_file_path, disk_file_path):
    if not os.path.exists(local_file_path):
        logger.error(f"Файл {local_file_path} не найден.")
        return
    
    yadisk_token = config.ya_disk_token.get_secret_value()
    y = yadisk.YaDisk(token=yadisk_token)
    
    if y.check_token():
        logger.info("Токен действителен, можно приступать к работе с файлами на Яндекс Диск.")
    else:
        logger.error("Токен недействителен, попробуйте получить его заново.")
        return
    
    try:
        y.upload(local_file_path, disk_file_path)
        logger.info(f"Файл {local_file_path} успешно загружен на Яндекс Диск.")
    except Exception as e:
        logger.error(f"Не удалось загрузить файл: {e}\n{traceback.format_exc()}")
        y.remove("/dashboard_data/user_actions.xlsx")
        y.upload("user_actions.xlsx", "/dashboard_data/user_actions.xlsx")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 31),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'export_user_actions',
    default_args=default_args,
    description='Экспорт данных из БД и загрузка на Яндекс Диск',
    schedule_interval='@hourly',
)

export_task = PythonOperator(
    task_id='export_to_excel_task',
    python_callable=export_to_excel,
    dag=dag,
)

upload_task = PythonOperator(
    task_id='upload_to_yadisk_task',
    python_callable=transfer_to_yadisk,
    op_args=["user_actions.xlsx", "/dashboard_data/user_actions.xlsx"],
    dag=dag,
)

export_task >> upload_task
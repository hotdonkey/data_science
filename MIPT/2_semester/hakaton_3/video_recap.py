from datetime import timedelta
import pysrt
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os

from collections import Counter

import random
from datetime import timedelta

import subprocess
import os
from datetime import timedelta

from transformers import pipeline

from moviepy import VideoFileClip
import os

import warnings
warnings.filterwarnings("ignore")

###########################################################################################


MODEL_NAME = "handler-bird/movie_genre_multi_classification"
SAVE_DIR = "./local_model"

# Проверяем, существует ли папка и файлы модели
if not os.path.exists(SAVE_DIR) or not os.listdir(SAVE_DIR):
    print("Модель не найдена локально. Скачиваю...")
    
    # Создаем папку, если её нет
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Скачиваем токенизатор и модель
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

    # Сохраняем локально
    tokenizer.save_pretrained(SAVE_DIR)
    model.save_pretrained(SAVE_DIR)
    
    print(f"Модель успешно сохранена в {SAVE_DIR}")
else:
    print(f"Модель уже существует в {SAVE_DIR}. Пропускаем скачивание.")
    

# Задаем переменные среды
LOCAL_MODEL_PATH = "./local_model"
VIDEO_DIR = "./data/vids"

##########################################################################################
##########################################################################################

class RecapVideoTransformer:
    """
    Класс для создания краткого обзора (recap) видео на основе анализа жанра и временных меток субтитров.

    Основные этапы работы:
    1. Загрузка субтитров.
    2. Определение жанра видео.
    3. Расчёт ключевых моментов в зависимости от жанра.
    4. Вырезание соответствующих фрагментов из видео.
    5. Склейка фрагментов в один итоговый файл.

    Атрибуты:
        file_name (str): Имя видеофайла без расширения.
        df (pd.DataFrame): Датафрейм с субтитрами (временные метки и текст).
        genre (str): Обнаруженный жанр видео.
        total_length (int): Длительность итогового рекэпа в секундах.
        recap (dict): Словарь с ключевыми моментами и временными рамками.
        clips_times (list): Список кортежей (start, end) для вырезания клипов.
        input_video_path (str): Путь к исходному видеофайлу.
        output_video_path (str): Путь к выходному видеофайлу.
        list_file (str): Путь к временному файлу списка клипов для FFmpeg.
    """

    # Словарь временных зон для разных жанров
    genre_dict = \
        {
            "drama": {
                "setup_conflict": {
                    "description": "Установление основного конфликта",
                    "start_percent": 5.0,
                    "end_percent": 15.0
                },
                "character_development": {
                    "description": "Эмоциональное развитие персонажа",
                    "start_percent": 20.0,
                    "end_percent": 40.0
                },
                "plot_twist": {
                    "description": "Поворот сюжета или неожиданное развитие",
                    "start_percent": 50.0,
                    "end_percent": 60.0
                },
                "climax_confrontation": {
                    "description": "Главный конфликт между героями",
                    "start_percent": 60.0,
                    "end_percent": 75.0
                },
                "partial_resolution": {
                    "description": "Частичное разрешение, но с продолжением",
                    "start_percent": 80.0,
                    "end_percent": 90.0
                },
                "cliffhanger": {
                    "description": "Неожиданный поворот или намёк на следующую серию",
                    "start_percent": 95.0,
                    "end_percent": 100.0
                }
            },

            "crime": {
                "crime_discovery": {
                    "description": "Обнаружение преступления или загадка",
                    "start_percent": 0.0,
                    "end_percent": 10.0
                },
                "gathering_clues": {
                    "description": "Расследование, сбор улик",
                    "start_percent": 15.0,
                    "end_percent": 35.0
                },
                "false_lead": {
                    "description": "Ложный след или неправильная версия",
                    "start_percent": 35.0,
                    "end_percent": 50.0
                },
                "truth_revealed": {
                    "description": "Открытие истинного преступника или причины",
                    "start_percent": 60.0,
                    "end_percent": 75.0
                },
                "resolution": {
                    "description": "Завершение дела или арест",
                    "start_percent": 80.0,
                    "end_percent": 90.0
                },
                "emotional_ending": {
                    "description": "Реакция главных героев или намёк на будущее",
                    "start_percent": 90.0,
                    "end_percent": 100.0
                }
            },

            "fantasy": {
                "quest_announced": {
                    "description": "Объявление цели или миссии",
                    "start_percent": 0.0,
                    "end_percent": 10.0
                },
                "trials": {
                    "description": "Пройденные испытания или битвы",
                    "start_percent": 10.0,
                    "end_percent": 50.0
                },
                "betrayal_or_failure": {
                    "description": "Предательство или крупная потеря",
                    "start_percent": 50.0,
                    "end_percent": 65.0
                },
                "power_or_knowledge_gained": {
                    "description": "Герои получают силу или знание для победы",
                    "start_percent": 65.0,
                    "end_percent": 80.0
                },
                "final_battle": {
                    "description": "Финальная битва с главным злом",
                    "start_percent": 80.0,
                    "end_percent": 95.0
                },
                "new_horizon": {
                    "description": "Намёк на новое приключение или путь",
                    "start_percent": 95.0,
                    "end_percent": 100.0
                }
            },

            "comedy": {
                "funny_situation_introduced": {
                    "description": "Введение забавной ситуации",
                    "start_percent": 0.0,
                    "end_percent": 10.0
                },
                "absurdity_increases": {
                    "description": "Усиление абсурда или ошибок",
                    "start_percent": 10.0,
                    "end_percent": 30.0
                },
                "peak_of_humor": {
                    "description": "Максимальный юмор, точка кульминации",
                    "start_percent": 30.0,
                    "end_percent": 50.0
                },
                "attempt_to_fix": {
                    "description": "Попытка исправить ситуацию",
                    "start_percent": 50.0,
                    "end_percent": 70.0
                },
                "unexpected_result": {
                    "description": "Неожиданный смешной результат",
                    "start_percent": 70.0,
                    "end_percent": 90.0
                },
                "ironic_conclusion": {
                    "description": "Шутка на прощание или клиффхенгер",
                    "start_percent": 90.0,
                    "end_percent": 100.0
                }
            },

            "sci-fi": {
                "technology_introduced": {
                    "description": "Введение нового явления или технологии",
                    "start_percent": 0.0,
                    "end_percent": 10.0
                },
                "consequences_explored": {
                    "description": "Изучение последствий использования",
                    "start_percent": 10.0,
                    "end_percent": 40.0
                },
                "ethical_dilemma": {
                    "description": "Моральный выбор или риск",
                    "start_percent": 40.0,
                    "end_percent": 60.0
                },
                "crisis_occurs": {
                    "description": "Происходит кризис или угроза",
                    "start_percent": 60.0,
                    "end_percent": 80.0
                },
                "solution_found": {
                    "description": "Находится решение или новое понимание",
                    "start_percent": 80.0,
                    "end_percent": 95.0
                },
                "philosophical_note": {
                    "description": "Философский вывод или вопрос",
                    "start_percent": 95.0,
                    "end_percent": 100.0
                }
            },

            "horror": {
                "atmosphere_set": {
                    "description": "Создание атмосферы страха",
                    "start_percent": 0.0,
                    "end_percent": 10.0
                },
                "first_fear": {
                    "description": "Первый страх или сигнал опасности",
                    "start_percent": 10.0,
                    "end_percent": 25.0
                },
                "tension_builds": {
                    "description": "Наращивание напряжения",
                    "start_percent": 25.0,
                    "end_percent": 50.0
                },
                "main_horror_moment": {
                    "description": "Главный момент ужаса или жертва",
                    "start_percent": 50.0,
                    "end_percent": 70.0
                },
                "escape_or_chase": {
                    "description": "Погоня или попытка спастись",
                    "start_percent": 70.0,
                    "end_percent": 85.0
                },
                "unresolved_end": {
                    "description": "Неожиданный финал или намёк на продолжение",
                    "start_percent": 85.0,
                    "end_percent": 100.0
                }
            },
            "default": {
                "setup": {
                    "description": "Введение основного конфликта или ситуации",
                    "start_percent": 5.0,
                    "end_percent": 15.0
                },
                "development": {
                    "description": "Развитие событий, углубление в сюжет",
                    "start_percent": 20.0,
                    "end_percent": 45.0
                },
                "plot_twist": {
                    "description": "Неожиданный поворот или осложнение",
                    "start_percent": 50.0,
                    "end_percent": 65.0
                },
                "climax": {
                    "description": "Кульминационный момент действия",
                    "start_percent": 70.0,
                    "end_percent": 85.0
                },
                "cliffhanger": {
                    "description": "Финальный намёк на следующую серию",
                    "start_percent": 90.0,
                    "end_percent": 100.0
                }
            }

        }

    # Единые ключевые моменты для всех жанров
    UNIFIED_KEY_MOMENTS = {
        "setup": {"description": "Введение основной ситуации или конфликта"},
        "development": {"description": "Развитие сюжета, углубление в историю"},
        "twist": {"description": "Неожиданный поворот или осложнение"},
        "climax": {"description": "Кульминационный момент"},
        "resolution": {"description": "Разрешение или намёк на продолжение"},
        "cliffhanger": {"description": "Финальное событие или клиффхенгер"}
    }

    def __init__(self, file_name: str):
        """
        Инициализация класса.

        Проверяет наличие необходимых файлов, определяет жанр,
        рассчитывает ключевые моменты и создаёт итоговое видео.

        Args:
            file_name (str): Имя видеофайла без расширения.
        """
        self.file_name = file_name

        # Проверяем существование файлов
        if not os.path.exists(f'./data/subtitles/{self.file_name}.srt'):
            raise FileNotFoundError(
                f"Subtitles file ./data/subtitles/{self.file_name}.srt not found")
        if not os.path.exists(f"./data/vids/{self.file_name}.mp4"):
            raise FileNotFoundError(
                f"Video file ./data/vids/{self.file_name}.mp4 not found")

        # Загрузка субтитров
        subs = pysrt.open(f'./data/subtitles/{self.file_name}.srt')
        self.df = pd.DataFrame([{
            'index': sub.index,
            'start': sub.start.to_time(),
            'end': sub.end.to_time(),
            'text': sub.text
        } for sub in subs])

        # Определение жанра видео
        classifier = pipeline(
            "text-classification",
            model=LOCAL_MODEL_PATH,
            tokenizer=LOCAL_MODEL_PATH,
            #model="handler-bird/movie_genre_multi_classification",
            #tokenizer="distilbert-base-uncased",
            framework="pt"
        )
        self.results = classifier(self.df["text"].tolist()[:100])
        self.genres = Counter([result["label"] for result in self.results])
        self.genre = self.genres.most_common(
            1)[0][0] if self.genres else 'default'

        # Получаем длительность видео
        self.duration = self.get_video_duration(
            f"./data/vids/{self.file_name}.mp4")
        self.total_length = max(self.duration - 4 * 60, 60)  # минимум 1 минута

        # Генерируем recap
        self.recap = self.generate_recap(self.genre, self.total_length)
        self.clips_times = self.get_borders(self.recap)

        # Устанавливаем пути
        self.input_video_path = f"./data/vids/{self.file_name}.mp4"
        self.output_video_path = f"./data/result/{self.file_name}_final_recap.mp4"
        self.list_file = "clips_list.txt"

        # Создаём список клипов и склеиваем их
        self.create_list_file(self.clips_times, self.list_file)
        self.concat_clips()

    def concat_clips(self):
        """
        Объединяет клипы в одно видео с помощью FFmpeg.
        После объединения временные файлы удаляются.
        """
        try:
            subprocess.run([
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", self.list_file,
                "-c", "copy",
                self.output_video_path,
                "-y"
            ], check=True)
        finally:
            # Очистка временных файлов
            for i in range(len(self.clips_times)):
                clip_path = f"clip_{i}.mp4"
                if os.path.exists(clip_path):
                    os.remove(clip_path)
            if os.path.exists(self.list_file):
                os.remove(self.list_file)

    def get_video_duration(self, file_path: str) -> float:
        """
        Возвращает длительность видео в секундах.

        Args:
            file_path (str): Путь к видеофайлу.

        Returns:
            float: Длительность видео в секундах.
        """
        with VideoFileClip(file_path) as clip:
            return clip.duration

    def time_to_seconds(self, time_str: str) -> int:
        """
        Преобразует строку времени формата hh:mm:ss в количество секунд.

        Args:
            time_str (str): Время в виде строки (например, "01:15:30").

        Returns:
            int: Время в секундах.
        """
        if isinstance(time_str, str):
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = parts
                s = s.split('.')[0]  # Отбрасываем миллисекунды
            elif len(parts) == 2:
                m, s = parts
                h = 0
            else:
                return 0
            return int(h) * 3600 + int(m) * 60 + int(s)
        return 0

    def create_list_file(self, clips: List[Tuple[str, str]], list_path: str):
        """
        Создаёт временный файл со списком клипов для FFmpeg.

        Args:
            clips (List[Tuple[str, str]]): Список кортежей (start_time, end_time).
            list_path (str): Путь к выходному файлу.
        """
        with open(list_path, "w") as f:
            for i, (start, end) in enumerate(clips):
                if not start or not end:
                    continue
                start_sec = self.time_to_seconds(start)
                end_sec = self.time_to_seconds(end)
                if start_sec >= end_sec:
                    continue
                clip_name = f"clip_{i}.mp4"
                subprocess.run([
                    "ffmpeg",
                    "-ss", str(start_sec),
                    "-to", str(end_sec),
                    "-i", self.input_video_path,
                    "-c", "copy",
                    clip_name,
                    "-y"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                f.write(f"file '{clip_name}'\n")

    def get_borders(self, recap_data: Dict[str, Dict]) -> List[Tuple[Optional[str], Optional[str]]]:
        """
        Извлекает временные границы клипов из данных рекэпа.

        Args:
            recap_data (Dict[str, Dict]): Результат функции generate_recap.

        Returns:
            List[Tuple[Optional[str], Optional[str]]]: Список кортежей (start, end).
        """
        return [
            (moment["clip_start"], moment["clip_end"])
            for moment in recap_data.values()
            if moment and moment.get("clip_start") and moment.get("clip_end")
        ]

    def unify_moments(self, genre_data: Dict[str, Dict]) -> Dict[str, Optional[str]]:
        """
        Приводит ключевые моменты конкретного жанра к унифицированному виду.

        Args:
            genre_data (Dict[str, Dict]): Жанровые ключевые моменты.

        Returns:
            Dict[str, Optional[str]]: Маппинг унифицированных ключевых моментов.
        """
        mapping = {key: None for key in self.UNIFIED_KEY_MOMENTS}
        for key in genre_data:
            key_lower = key.lower()
            if "setup" in key_lower or "introduced" in key_lower:
                mapping["setup"] = key
            elif "develop" in key_lower or "gathering" in key_lower:
                mapping["development"] = key
            elif "twist" in key_lower or "false" in key_lower:
                mapping["twist"] = key
            elif "climax" in key_lower or "battle" in key_lower:
                mapping["climax"] = key
            elif "resolution" in key_lower or "ending" in key_lower:
                mapping["resolution"] = key
            elif "cliffhanger" in key_lower or "hint" in key_lower:
                mapping["cliffhanger"] = key
        return mapping

    def generate_recap(self, genre: str, total_seconds: int, chunk_duration: int = 20) -> Dict[str, Dict]:
        """
        Генерирует словарь с ключевыми моментами видео по жанру.

        Args:
            genre (str): Жанр видео.
            total_seconds (int): Общая длина рекэпа в секундах.
            chunk_duration (int): Длительность каждого фрагмента в секундах.

        Returns:
            Dict[str, Dict]: Словарь с ключевыми моментами и временными рамками.
        """
        def seconds_to_time(seconds):
            return str(timedelta(seconds=seconds))

        genre_data = self.genre_dict.get(
            genre.lower(), self.genre_dict["default"])
        mapping = self.unify_moments(genre_data)
        unified_moments = {}

        for unified_key, genre_key in mapping.items():
            if not genre_key:
                continue
            event = genre_data.get(genre_key)
            if not event:
                continue
            start_time = max(
                0, round(total_seconds * event["start_percent"] / 100))
            end_time = min(total_seconds, round(
                total_seconds * event["end_percent"] / 100))
            clip_start_sec = None
            clip_end_sec = None
            if end_time - start_time >= chunk_duration:
                clip_start_sec = random.randint(
                    start_time, end_time - chunk_duration)
                clip_end_sec = clip_start_sec + chunk_duration
            unified_moments[unified_key] = {
                "description": event["description"],
                "start": seconds_to_time(start_time),
                "end": seconds_to_time(end_time),
                "clip_start": seconds_to_time(clip_start_sec) if clip_start_sec else None,
                "clip_end": seconds_to_time(clip_end_sec) if clip_end_sec else None,
            }

        return unified_moments
    

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    
    # Получаем все .mp4 файлы в указанной директории
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")]

    for video_file in video_files:
        # Убираем расширение, получаем file_name
        file_name = os.path.splitext(video_file)[0]

        # Формируем пути
        subtitle_path = f"./data/subtitles/{file_name}.srt"
        video_path = f"./data/vids/{file_name}.mp4"

        # Проверяем существование субтитров
        if not os.path.exists(subtitle_path):
            print(f"Субтитры для {file_name} не найдены. Пропускаем.")
            continue

        if not os.path.exists(video_path):
            print(f"Видео для {file_name} не найдено. Пропускаем.")
            continue

        # Обрабатываем видео
        print(f"🎬 Обрабатываем: {file_name}")
        try:
            recap_video = RecapVideoTransformer(file_name)
            print(f"Готово: {file_name}")
        except Exception as e:
            print(f"Ошибка при обработке {file_name}: {e}")
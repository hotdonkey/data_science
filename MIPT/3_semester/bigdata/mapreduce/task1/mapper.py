#!/usr/bin/env python3

import sys
import json
from datetime import datetime
import io

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def parse_time(time_str):
    """Парсит время в формате H:MM или HH:MM, нормализует однозначные минуты"""
    try:
        # Нормализуем формат времени (например, "15:0" -> "15:00")
        parts = time_str.strip().split(':')
        if len(parts) != 2:
            return None
            
        hours = parts[0].strip()
        minutes = parts[1].strip()
        
        # Добавляем ведущий ноль к минутам если нужно
        if len(minutes) == 1:
            minutes = '0' + minutes
            
        normalized_time = f"{hours}:{minutes}"
        return datetime.strptime(normalized_time, "%H:%M").time()
    except:
        return None

def calculate_daily_minutes(day_schedule):
    """Вычисляет количество минут работы за один день"""
    if not day_schedule or day_schedule == "0:0-0:0":
        return 0
        
    try:
        parts = day_schedule.split("-")
        if len(parts) != 2:
            return 0

        start_str, end_str = parts[0].strip(), parts[1].strip()
        
        start_time = parse_time(start_str)
        end_time = parse_time(end_str)
        
        if not start_time or not end_time:
            return 0

        start_min = start_time.hour * 60 + start_time.minute
        end_min = end_time.hour * 60 + end_time.minute

        if end_min < start_min:
            # Работа после полуночи
            return (24 * 60 - start_min) + end_min
        else:
            return end_min - start_min
    except:
        return 0

def timecounter(business_id, hours, is_opened):
    """Основная функция подсчета времени работы"""
    # Если бизнес закрыт, возвращаем 0
    if is_opened == 0:
        return f"{business_id}\t0"

    # Если нет расписания, возвращаем 0
    if not hours:
        return f"{business_id}\t0"

    total_minutes = 0
    
    # Суммируем минуты по всем дням недели
    for day_schedule in hours.values():
        day_minutes = calculate_daily_minutes(day_schedule)
        total_minutes += day_minutes

    return f"{business_id}\t{total_minutes}"

# Основной цикл обработки
for line in input_stream:
    line = line.strip()
    if not line:
        continue
        
    try:
        business = json.loads(line)
        business_id = business.get("business_id")
        
        if not business_id:
            continue
            
        hours = business.get("hours")
        is_opened = business.get("is_open", 1)  # По умолчанию считаем открытым
        
        # Преобразуем в int, обрабатывая случай когда значение None
        try:
            is_opened = int(is_opened)
        except (TypeError, ValueError):
            is_opened = 1  # Если не можем преобразовать, считаем открытым

        result = timecounter(business_id, hours, is_opened)
        print(result, file=output_stream)

    except Exception as e:
        # В случае любой ошибки выводим 0 минут
        business_id = business.get("business_id") if 'business' in locals() else "unknown"
        if business_id != "unknown":
            print(f"{business_id}\t0", file=output_stream)
        continue
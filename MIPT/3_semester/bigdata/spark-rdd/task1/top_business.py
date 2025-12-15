#!/usr/bin/env python3

import sys
import json
from datetime import datetime
from pyspark import SparkContext

def timecounter(business_id, hours):
    """Наша вечная функция с небольгими изменениями"""
    # проверяем 
    if not hours:
        return (business_id, 0)

    total_minutes = 0
    try:
        for day_hours in hours.values():
            if day_hours == "0:0-0:0":
                continue

            parts = day_hours.split("-")
            if len(parts) != 2:
                continue

            start_str, end_str = parts[0].strip(), parts[1].strip()

            # Обработка времени в формате H:M или HH:MM
            start = datetime.strptime(start_str, "%H:%M").time()
            end = datetime.strptime(end_str, "%H:%M").time()

            start_min = start.hour * 60 + start.minute
            end_min = end.hour * 60 + end.minute

            if end_min < start_min:
                # Работа заполночь
                total_minutes += (24 * 60 - start_min) + end_min
            else:
                total_minutes += end_min - start_min

    except (ValueError, AttributeError, TypeError):
        return (business_id, 0)

    return (business_id, total_minutes)

def process_business(line):
    """Обрабатывает одну строку бизнеса с использованием нашей вечной функции"""
    try:
        data = json.loads(line)
        business_id = data.get('business_id', '')
        hours = data.get('hours', {})
        
        # Используем timecounter
        return timecounter(business_id, hours)
    except:
        return (None, 0)

def main():
    output_path = sys.argv[1]
    
    sc = SparkContext(appName="BusinessHours")
    
    try:
        # Загружаем данные о бизнесах
        business_rdd = sc.textFile("/data/yelp/business")
        
        # Вычисляем общее время работы для каждого бизнеса
        business_hours = business_rdd.map(process_business) \
            .filter(lambda x: x[0] is not None) \
            .reduceByKey(lambda a, b: a + b) 
        
        # Сортируем: сначала по минутам (убывание), потом по business_id (возрастание)
        sorted_business = business_hours.sortBy(
            lambda x: (-x[1], x[0])
        )
        
        # Сохраняем все данные в HDFS
        sorted_business.saveAsTextFile(output_path)
        
        # Выводим топ-10
        top10 = sorted_business.take(10)
        for business_id, minutes in top10:
            print(f"{business_id}\t{minutes}")
            
    finally:
        sc.stop()

if __name__ == "__main__":
    main()
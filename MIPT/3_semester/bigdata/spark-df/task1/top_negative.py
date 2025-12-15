#!/usr/bin/env python3

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc
from pyspark.sql.window import Window
from pyspark.sql import functions as F

def main(output_folder):
    # Создаем SparkSession
    spark = SparkSession.builder \
        .appName("TopNegativeReviews") \
        .getOrCreate()
    
    # Загружаем данные
    review = spark.read.json("/data/yelp/review")
    business = spark.read.json("/data/yelp/business")
    
    # Фильтруем негативные отзывы (stars < 3)
    negative_reviews = review.filter(col("stars") < 3)
    
    # Присоединяем бизнесы, чтобы получить город
    review_with_city = negative_reviews.join(
        business.select("business_id", "city"),
        "business_id",
        "inner"
    )
    
    # Группируем по business_id и city, считаем количество негативных отзывов
    business_negative_counts = review_with_city.groupBy("business_id", "city") \
        .agg(count("*").alias("negative_cnt"))
    
    # Определяем оконную функцию для ранжирования внутри каждого города
    window_spec = Window.partitionBy("city") \
        .orderBy(desc("negative_cnt"))
    
    # Добавляем ранг и фильтруем топ-10 для каждого города
    top_10_per_city = business_negative_counts \
        .withColumn("rank", F.rank().over(window_spec)) \
        .filter(col("rank") <= 10) \
        .drop("rank")
    
    # Сортируем результат для удобства чтения
    result = top_10_per_city.orderBy("city", desc("negative_cnt"))
    
    # Сохраняем результат 
    result.write \
        .mode("overwrite") \
        .option("delimiter", "\t") \
        .option("header", "false") \
        .csv(output_folder)

    spark.stop()


if __name__ == "__main__":   
    output_folder = sys.argv[1]
    main(output_folder)
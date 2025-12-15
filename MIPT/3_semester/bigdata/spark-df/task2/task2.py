#!/usr/bin/env python3

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    explode,
    split,
    trim,
    to_date,
    date_format,
    count
)

def main(output_folder):
    spark = SparkSession.builder.appName("CheckinsByCategory").master("yarn").getOrCreate()

    # Загружаем даныне
    business_df = (spark.read.format("json").load("/data/yelp/business"))
    checkins_df = (spark.read.format("json").load("/data/yelp/checkin"))
    
    # Парсинг категорий
    business_exploded = business_df.select(
        col("business_id"),
        explode(split(col("categories"), ",")).alias("category")
    ).withColumn("category", trim(col("category")))
    
    # Парсинг дат из checkins: разбиваем, конвертируем, извлекаем месяц
    checkins_parsed = checkins_df.select(
        col("business_id"),
        explode(split(col("date"), ",")).alias("visit_date_str")
    ).withColumn(
        "visit_date_str_clean",  # добавляем очищенную колонку
        trim(col("visit_date_str"))
    ).withColumn(
        "visit_date",
        to_date(col("visit_date_str_clean"), "yyyy-MM-dd HH:mm:ss")
    ).filter(
        col("visit_date").isNotNull()
    ).withColumn(
        "mnth",
        date_format(col("visit_date"), "yyyy-MM")
    ).drop("visit_date_str", "visit_date_str_clean") 
    
    # Объединение и агрегация
    joined = checkins_parsed.join(business_exploded, on="business_id")
    result = joined.groupBy("mnth", "category") \
                    .agg(count("*").alias("checkins")) \
                    .orderBy("mnth", "category")
    
    result.rdd.map(lambda row: f"{row.mnth}\t{row.category}\t{row.checkins}") \
          .coalesce(1) \
          .saveAsTextFile(sys.argv[1] if len(sys.argv) > 1 else "output")
    
    spark.stop()
    
if __name__ == "__main__":   
    output_folder = sys.argv[1]
    main(output_folder)
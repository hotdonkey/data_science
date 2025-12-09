-- БД 
USE ${hiveconf:DB_NAME};

-- Банка
ADD JAR /opt/hive/lib/hive-hcatalog-core-3.1.3.jar;

-- Таблица бизнесов --
-- Зачищаем если было
DROP TABLE IF EXISTS business_raw;

-- Создаем новую
CREATE EXTERNAL TABLE business_raw (
    business_id STRING,
    city STRING
)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
STORED AS TEXTFILE
LOCATION '/data/yelp/business';

-- Таблица отзывов --
-- Зачищаем если было
DROP TABLE IF EXISTS review_raw;

-- Создаем новую
CREATE EXTERNAL TABLE review_raw (
    business_id STRING,
    stars DOUBLE
)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
STORED AS TEXTFILE
LOCATION '/data/yelp/review';

-- Запрос
SELECT
    business_id,
    city,
    neg_count
FROM (
    SELECT
        b.business_id,
        b.city,
        COUNT(*) AS neg_count,
        ROW_NUMBER() OVER (PARTITION BY b.city ORDER BY COUNT(*) DESC, b.business_id ASC) AS rn
    FROM review_raw r
    JOIN business_raw b ON r.business_id = b.business_id
    WHERE r.stars < 3.0
      AND b.city IS NOT NULL
    GROUP BY b.business_id, b.city
) t
WHERE rn <= 10
ORDER BY city, neg_count DESC, business_id;
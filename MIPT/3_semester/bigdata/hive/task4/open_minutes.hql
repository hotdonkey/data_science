USE ${hiveconf:DB_NAME};

-- Внешняя таблица
DROP TABLE IF EXISTS business_raw;
CREATE EXTERNAL TABLE business_raw (raw_line STRING)
STORED AS TEXTFILE
LOCATION '/data/yelp/business';

-- Файл маппера просто взяд из mapreduce - там то он рабочий был хоть и страшненький
ADD FILE ./mapper.py;

-- Запрос
SELECT TRANSFORM(raw_line)
USING 'mapper.py'
AS (business_id STRING, open_minutes INT)
FROM business_raw;
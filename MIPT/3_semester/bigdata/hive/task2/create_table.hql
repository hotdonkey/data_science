USE ${hiveconf:DB_NAME};

DROP TABLE IF EXISTS business_raw;

CREATE EXTERNAL TABLE business_raw (raw_line STRING)
STORED AS TEXTFILE
LOCATION '/data/yelp/business';

ADD FILE ./mapper.py;

SELECT attr, COUNT(attr) AS cnt
FROM (
    SELECT TRANSFORM(raw_line)
    USING 'mapper.py'
    AS (attr STRING)
    FROM business_raw
    WHERE raw_line LIKE '%"attributes"%'
) t
GROUP BY attr
ORDER BY attr
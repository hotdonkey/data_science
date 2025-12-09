-- SET hive.execution.engine=mr;
-- ADD JAR /usr/lib/hive/lib/hive-hcatalog-core-3.1.2.jar;
-- USE DATABASE student00_yelp;

CREATE DATABASE IF NOT EXISTS ${hiveconf:DB_NAME}
LOCATION '${hiveconf:DB_PATH}';
# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import json
import argparse
import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from collections import defaultdict


CONFIG_PATH = "config.yaml"


def load_config(config_path):
    """Load full config from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def ensure_fresh_hbase_table(conn, table_name, cf_dict):
    tables = [t.decode() for t in conn.tables()]
    if table_name in tables:
        print(f"Удаляем существующую таблицу '{table_name}'...")
        conn.disable_table(table_name)
        conn.delete_table(table_name)
    conn.create_table(table_name, cf_dict)
    print(f"Таблица '{table_name}' создана.")


def write_to_hbase(time_map, hbase_cfg):
    import happybase

    host = hbase_cfg.get("host", "localhost")
    port = hbase_cfg.get("port", 9090)
    table_name = hbase_cfg.get("table", "pubg_kill_stats")
    cf_dict = {'wp': dict()}

    try:
        conn = happybase.Connection(host=host, port=port)
        ensure_fresh_hbase_table(conn, table_name, cf_dict)
        table = conn.table(table_name)

        with table.batch(batch_size=1000) as b:
            for t, weapons in time_map.items():
                row_key = "{:08d}".format(t).encode()
                row_data = {
                    "wp:{}".format(weapon).encode(): str(kills).encode()
                    for weapon, kills in weapons.items()
                }
                b.put(row_key, row_data)
        conn.close()
        print("Данные записаны в HBase")
    except Exception as e:
        print("Ошибка записи в HBase: {}".format(e))


def write_to_cassandra(time_map, cassandra_cfg):
    from cassandra.cluster import Cluster
    from cassandra import ConsistencyLevel

    contact_points = cassandra_cfg.get("contact_points", ["127.0.0.1"])
    port = cassandra_cfg.get("port", 9042)
    keyspace = cassandra_cfg.get("keyspace", "pubg")
    table = cassandra_cfg.get("table", "kill_stats_v2")

    try:
        cluster = Cluster(
            contact_points=contact_points,
            port=port,
            connect_timeout=30,
            control_connection_timeout=30,
        )
        session = cluster.connect()
        
        session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {keyspace}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
        """)
        session.set_keyspace(keyspace)

        session.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                bucket int,
                time_sec int,
                weapon text,
                kills int,
                PRIMARY KEY (bucket, time_sec, weapon)
            ) WITH CLUSTERING ORDER BY (time_sec ASC, weapon ASC)
        """)

        insert_stmt = session.prepare(
            f"INSERT INTO {table} (bucket, time_sec, weapon, kills) VALUES (?, ?, ?, ?)"
        )
        insert_stmt.consistency_level = ConsistencyLevel.ONE

        total = 0
        BATCH_SIZE = 100
        for t, weapons in time_map.items():
            bucket = t // 1000
            for weapon, kills in weapons.items():
                session.execute(insert_stmt, (bucket, t, weapon, kills))
                total += 1
                if total % BATCH_SIZE == 0:
                    print(f"Записано {total} строк...")

        print(f"Всего записано {total} строк в Cassandra")
        cluster.shutdown()
    except Exception as e:
        print("Ошибка записи в Cassandra: {}".format(e))


def write_to_minio(time_map, s3_path, minio_cfg):
    if not s3_path or not minio_cfg:
        return

    import boto3
    from io import BytesIO

    if not s3_path.startswith(("s3://", "s3a://")):
        raise ValueError("s3_path must start with 's3://' or 's3a://'")
    prefix_len = len("s3://") if s3_path.startswith("s3://") else len("s3a://")
    bucket, obj_key = s3_path[prefix_len:].split("/", 1)

    hierarchical_data = {"{:08d}".format(t): wp_dict for t, wp_dict in time_map.items()}
    s3 = boto3.client(
        's3',
        endpoint_url=minio_cfg["endpoint_url"],
        aws_access_key_id=minio_cfg["access_key"],
        aws_secret_access_key=minio_cfg["secret_key"],
    )

    json_str = json.dumps(hierarchical_data, ensure_ascii=False, indent=2)
    s3.upload_fileobj(BytesIO(json_str.encode('utf-8')), bucket, obj_key)
    print("Данные загружены в MinIO: s3://{}/{}".format(bucket, obj_key))


def main(config_path, s3_path):
    spark = SparkSession.builder \
        .appName("PUBG Writer") \
        .getOrCreate()

    # Чтение из HDFS
    df = spark.read.option("header", "true").csv("hdfs://master.hadoop.akhcheck.ru/data/pubg")
    df = df.filter(col("killer_name") != col("victim_name"))
    df = df.withColumn("time_sec", col("time").cast("int"))

    weapon_events = df.groupBy("time_sec", "killed_by").count().withColumnRenamed("count", "kills")
    rows = weapon_events.collect()
    spark.stop()

    # Построение time_map
    time_map = defaultdict(dict)
    for row in rows:
        t = row.time_sec
        wpn = row.killed_by
        cnt = row.kills
        time_map[t][wpn] = cnt

    # Загрузка конфигурации
    config = load_config(config_path)

    # Запись в HBase
    hbase_cfg = config.get("hbase")
    if hbase_cfg and isinstance(hbase_cfg, dict):
        write_to_hbase(time_map, hbase_cfg)

    # Запись в Cassandra
    cassandra_cfg = config.get("cassandra")
    if cassandra_cfg and isinstance(cassandra_cfg, dict):
        write_to_cassandra(time_map, cassandra_cfg)

    # Запись в MinIO
    minio_cfg = config.get("minio")
    if s3_path and minio_cfg:
        write_to_minio(time_map, s3_path, minio_cfg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--s3-path", default=None, help="MinIO/S3 path, e.g. s3://bucket/key.json")
    args = parser.parse_args()
    main(CONFIG_PATH, args.s3_path)
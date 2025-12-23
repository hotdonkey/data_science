# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import argparse
import yaml
import json
from collections import defaultdict


CONFIG_PATH = "config.yaml"


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ================ HBase ================
def read_from_hbase(config, from_sec, to_sec):
    hbase_cfg = config.get("hbase")
    if not hbase_cfg:
        raise RuntimeError("HBase config missing")

    import happybase
    conn = happybase.Connection(
        host=hbase_cfg.get("host", "localhost"),
        port=hbase_cfg.get("port", 9090)
    )
    table = conn.table(hbase_cfg.get("table", "pubg_kill_stats"))

    start_key = "{:08d}".format(from_sec)
    end_key = "{:08d}".format(to_sec + 1)

    totals = defaultdict(int)
    for key, data in table.scan(row_start=start_key.encode(), row_stop=end_key.encode()):
        for col, val in data.items():
            try:
                weapon = col.decode().split(':', 1)[1]
                totals[weapon] += int(val.decode())
            except Exception:
                continue
    conn.close()
    return dict(totals)

# ================ Cassandra ================
def read_from_cassandra(config, from_sec, to_sec):
    from collections import defaultdict 

    cassandra_cfg = config.get("cassandra")
    if not cassandra_cfg:
        raise RuntimeError("Cassandra config missing")

    from cassandra.cluster import Cluster
    contact_points = cassandra_cfg.get("contact_points", ["127.0.0.1"])
    port = cassandra_cfg.get("port", 9042)
    keyspace = cassandra_cfg.get("keyspace", "pubg")
    table = cassandra_cfg.get("table", "kill_stats_v2")

    cluster = Cluster(contact_points=contact_points, port=port)
    session = cluster.connect(keyspace)

    start_bucket = from_sec // 1000
    end_bucket = to_sec // 1000

    totals = defaultdict(int)

    for bucket in range(start_bucket, end_bucket + 1):
        query = f"""
            SELECT time_sec, weapon, kills
            FROM {table}
            WHERE bucket = {bucket}
              AND time_sec >= {from_sec}
              AND time_sec <= {to_sec}
        """
        rows = session.execute(query)
        for row in rows:
            totals[row.weapon] += row.kills

    cluster.shutdown()
    return dict(totals)


# ================ MinIO ================
def read_from_minio(config, s3_path, from_sec, to_sec):
    if not s3_path:
        raise ValueError("--s3-path is required for MinIO fallback")

    minio_cfg = config.get("minio")
    if not minio_cfg:
        raise RuntimeError("MinIO config missing")

    import boto3
    prefix_len = len("s3://") if s3_path.startswith("s3://") else len("s3a://")
    bucket, key = s3_path[prefix_len:].split("/", 1)

    s3 = boto3.client(
        's3',
        endpoint_url=minio_cfg["endpoint_url"],
        aws_access_key_id=minio_cfg["access_key"],
        aws_secret_access_key=minio_cfg["secret_key"],
    )

    obj = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(obj['Body'].read().decode('utf-8'))

    totals = defaultdict(int)
    for time_str, weapons in data.items():
        t = int(time_str)
        if from_sec <= t <= to_sec:
            for wpn, kills in weapons.items():
                totals[wpn] += kills
    return dict(totals)


# ================ Main ================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("from_sec", type=int, help="Start second (inclusive)")
    parser.add_argument("to_sec", type=int, help="End second (inclusive)")
    parser.add_argument("--s3-path", default=None, help="S3 path for fallback")
    args = parser.parse_args()

    config = load_config(CONFIG_PATH)

    # Попытка 1: HBase
    try:
        print("+++ Чтение из HBase...", end=" ", flush=True)
        result = read_from_hbase(config, args.from_sec, args.to_sec)
        print("OK")
        for w in sorted(result):
            print("{}: {}".format(w, result[w]))
        return
    except Exception as e:
        print("FAIL ({})".format(str(e)[:60]))

    # Попытка 2: Cassandra
    try:
        print("+++ Чтение из Cassandra...", end=" ", flush=True)
        result = read_from_cassandra(config, args.from_sec, args.to_sec)
        print("OK")
        for w in sorted(result):
            print("{}: {}".format(w, result[w]))
        return
    except Exception as e:
        print("FAIL ({})".format(str(e)[:60]))

    # Попытка 3: MinIO
    try:
        print("+++ Чтение из MinIO...", end=" ", flush=True)
        result = read_from_minio(config, args.s3_path, args.from_sec, args.to_sec)
        print("OK")
        for w in sorted(result):
            print("{}: {}".format(w, result[w]))
        return
    except Exception as e:
        print("FAIL")
        print("Все источники недоступны: {}".format(e))


if __name__ == "__main__":
    main()
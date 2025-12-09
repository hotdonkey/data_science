#!/bin/bash
if [ $# -ne 2 ]; then
    echo "Usage: $0 <db_name> <db_path>"
    exit 1
fi

DB_NAME=$1
DB_PATH=$2

hive --hiveconf DB_NAME="$DB_NAME" --hiveconf DB_PATH="$DB_PATH" -f create_db.hql
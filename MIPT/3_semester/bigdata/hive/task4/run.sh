#!/bin/bash
set -e

DB_NAME=$1
cd "$(dirname "$0")"
hive --hiveconf DB_NAME="$DB_NAME" -f open_minutes.hql
#!/bin/bash
set -e

DB_NAME=$1

hive --hiveconf DB_NAME="$DB_NAME" -f create_table.hql
#!/bin/bash

DIR_IN="$1"
N_ROWS="$2"
DIR_OUT="$3"
REPLICAS="$4"

TMP_FILE=$(mktemp)

hdfs dfs -cat "$DIR_IN" 2>/dev/null | head -n "$N_ROWS" > "$TMP_FILE"
hdfs dfs -rm -f "$DIR_OUT" 2>/dev/null
hdfs dfs -mkdir -p "$(dirname "$DIR_OUT")" 2>/dev/null
hdfs dfs -put "$TMP_FILE" "$DIR_OUT"
hdfs dfs -setrep "$REPLICAS" "$DIR_OUT" 2>/dev/null

rm -f "$TMP_FILE"
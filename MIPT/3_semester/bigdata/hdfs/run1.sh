#!/bin/bash

DIR="$1"
NICK="kirill.kuznetsov.1"

hdfs dfs -mkdir -p "$DIR"
echo "$NICK" | hdfs dfs -put - "$DIR/README.md"

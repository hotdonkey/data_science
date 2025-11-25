#!/bin/bash

OUT_DIR=$1
NUM_REDUCERS=2
TMP_DIR="/tmp/task3_stage1_$$"

hdfs dfs -rm -r -skipTrash $OUT_DIR* $TMP_DIR* 2>/dev/null

yarn jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name="kk_task3_job" \
    -D mapreduce.job.reduces=${NUM_REDUCERS} \
    -files mapper.py,reducer.py \
    -mapper "mapper.py" \
    -reducer "reducer.py" \
    -input /data/yelp/review \
    -input /data/yelp/user \
    -output "$TMP_DIR"


yarn jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name="task3_stage2_sort" \
    -D mapreduce.job.reduces=${NUM_REDUCERS} \
    -files mapper_sort.py,reducer_sort.py \
    -mapper "mapper_sort.py" \
    -reducer "reducer_sort.py" \
    -input "$TMP_DIR" \
    -output "$OUT_DIR"

hdfs dfs -rm -r -skipTrash $TMP_DIR

hdfs dfs -cat "$OUT_DIR"/* | head -n 5
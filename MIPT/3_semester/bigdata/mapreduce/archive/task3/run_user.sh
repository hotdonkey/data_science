#!/usr/bin/env bash

OUT_DIR=$1
NUM_REDUCERS=2

hdfs dfs -rm -r -skipTrash $OUT_DIR*

yarn jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name="kk_task3_job" \
    -D mapreduce.job.reduces=${NUM_REDUCERS} \
    -files mapper.py,reducer.py \
    -mapper "./mapper.py" \
    -reducer "./reducer.py" \
    -input /data/yelp/user \
    -output $OUT_DIR

hdfs dfs -cat $OUT_DIR/* | head -n 5 2>/dev/null


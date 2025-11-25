#!/bin/bash

OUT_DIR=$1
NUM_REDUCERS=2

hdfs dfs -rm -r -skipTrash $OUT_DIR*

yarn jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name="kk_task1_job" \
    -D mapreduce.job.reduces=${NUM_REDUCERS} \
    -files mapper.py \
    -mapper "./mapper.py" \
    -input /data/yelp/business \
    -output $OUT_DIR


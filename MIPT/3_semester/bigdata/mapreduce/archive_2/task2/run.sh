#!/bin/bash

OUT_DIR=$1
NUM_REDUCERS=1

hdfs dfs -rm -r -skipTrash $OUT_DIR* 2>/dev/null

yarn jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name="kk_task2_job" \
    -D mapreduce.job.reduces=${NUM_REDUCERS} \
    -D stream.num.map.output.key.fields=3 \
    -D mapreduce.job.output.key.comparator.class=org.apache.hadoop.mapreduce.lib.partition.KeyFieldBasedComparator \
    -D mapreduce.partition.keycomparator.options="-k1,1nr -k2,2" \
    -files mapper.py,reducer.py \
    -mapper "mapper.py" \
    -reducer "reducer.py" \
    -input /data/yelp/business \
    -output $OUT_DIR
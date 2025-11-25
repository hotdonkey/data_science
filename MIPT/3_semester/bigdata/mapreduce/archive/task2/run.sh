#!/bin/bash

OUT_DIR=$1
NUM_REDUCERS=3

hdfs dfs -rm -r -skipTrash $OUT_DIR*

yarn jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name="kk_task2_job" \
    -D mapreduce.job.reduces=${NUM_REDUCERS} \
    -D stream.map.output.field.separator='\t' \
    -D stream..num.map.output.key.fields=2 \
    -D mapreduce.job.output.key.comparator.class=org.apache.hadoop.mapreduce.lib.partition.KeyFieldBasedComparator \
    -D mapreduce.partition.keycomparator.options="-k2,2nr -k1,1" \
    -files mapper.py,reducer.py \
    -mapper "./mapper.py" \
    -reducer "./reducer.py" \
    -input /data/yelp/business \
    -output $OUT_DIR

hdfs dfs -cat $OUT_DIR/* | head -n 10 2>/dev/null


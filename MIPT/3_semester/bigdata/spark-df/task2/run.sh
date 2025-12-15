#!/bin/bash

OUTPUT_FOLDER=$1

spark-submit \
    --master yarn \
    --deploy-mode cluster \
    --num-executors 2 \
    --executor-cores 1 \
    --executor-memory 512M \
    --driver-memory 512M \
    --conf spark.yarn.executor.memoryOverhead=128 \
    --conf spark.yarn.driver.memoryOverhead=128 \
    task2.py $OUTPUT_FOLDER

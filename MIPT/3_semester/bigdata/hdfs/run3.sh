#!/bin/bash

FILE="$1"

hdfs fsck "$FILE" -blocks 2>/dev/null | grep "Total blocks (validated):" | awk '{print $4}'

#!/bin/bash

FILE="$1"

hdfs fsck "$FILE" -files -blocks -locations 2>/dev/null \
  | grep "^0\." \
  | sed -E 's/.*\[([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+):.*/\1/'

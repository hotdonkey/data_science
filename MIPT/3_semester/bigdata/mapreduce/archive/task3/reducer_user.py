#!/usr/bin/env python3

import sys
import io

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
stderr_stream = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


for line in input_stream:
    try:
        user_id, friends = line.strip().split('\t')
        friends = int(friends)
        print(f"{user_id}\t{friends}", file=output_stream)
    except:
        continue

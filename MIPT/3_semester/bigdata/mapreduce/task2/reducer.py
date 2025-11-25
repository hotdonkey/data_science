#!/usr/bin/env python3

import sys
import io

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

results = []
count = 0

for line in input_stream:
    try:
        parts = line.strip().split('\t')
        if len(parts) == 3:
            business_id = parts[1]
            minutes = int(parts[2])
            results.append((business_id, minutes))
            count += 1
    except:
        continue

results.sort(key=lambda x: (-x[1], x[0]))

for business_id, minutes in results[:10]:
    print(f"{business_id}\t{minutes}", file=output_stream)
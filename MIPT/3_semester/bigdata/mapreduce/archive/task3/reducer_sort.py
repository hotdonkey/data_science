#!/usr/bin/env python3

import sys
import io
from heapq import nlargest

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
stderr_stream = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

data = []
for line in input_stream:
    parts = line.strip().split('\t')
    if len(parts) == 3:
        user_id, useful_sum, num_friends = parts
        data.append((int(useful_sum), user_id, int(num_friends)))

# Сортировка: по useful_sum убывание, затем user_id возрастание
data.sort(key=lambda x: (-x[0], x[1]))

for useful_sum, user_id, num_friends in data:
    print(f"{user_id}\t{useful_sum}\t{num_friends}")
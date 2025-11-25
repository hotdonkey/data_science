#!/usr/bin/env python3

import sys
import io

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
stderr_stream = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# results = []

for line in input_stream:#sys.stdin:
    try:
        business_id, minutes, _ = line.strip().split('\t')
        minutes = int(minutes)
        # results.append((business_id, int(minutes)))
        print(f"{business_id}\t{minutes}", file=output_stream)
    except:
        continue

# # Старая версия - сохранил как бэкап
# # Сортируем по убыванию минут, затем по возрастанию business_id
# results.sort(key=lambda x: (-x[1], x[0]))

# # Выводим топ-10
# for business_id, minutes in results[:10]:
#     print(f"{business_id}\t{minutes}", file=output_stream)
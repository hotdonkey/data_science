#!/usr/bin/env python3

import sys
import json
from datetime import datetime
import io

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
stderr_stream = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

def timecounter(business_id, hours):
    # проверяем 
    if not hours:
        return f"{business_id}\t0"

    total_minutes = 0
    try:
        for day_hours in hours.values():
            if day_hours == "0:0-0:0":
                continue

            parts = day_hours.split("-")
            if len(parts) != 2:
                continue

            start_str, end_str = parts[0].strip(), parts[1].strip()

            # Обработка времени в формате H:M или HH:MM
            start = datetime.strptime(start_str, "%H:%M").time()
            end = datetime.strptime(end_str, "%H:%M").time()

            start_min = start.hour * 60 + start.minute
            end_min = end.hour * 60 + end.minute

            if end_min < start_min:
                # Работа заполночь
                total_minutes += (24 * 60 - start_min) + end_min
            else:
                total_minutes += end_min - start_min

    except (ValueError, AttributeError, TypeError):
        return f"{business_id}\t0"

    return f"{business_id}\t{total_minutes}"

for line in input_stream:#sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        business = json.loads(line)
        business_id = business.get("business_id")
        hours = business.get("hours")
        is_open = business.get("is_open", 0)

        if business_id is None:
            continue
        
        if is_open == 0:
            print(f"{business_id}\t0", file=output_stream)
        else:
            result = timecounter(business_id, hours)
            print(result, file=output_stream)

    except Exception:
        continue
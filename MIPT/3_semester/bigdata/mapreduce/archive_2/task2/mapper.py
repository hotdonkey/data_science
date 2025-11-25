#!/usr/bin/env python3

import sys
import json
from datetime import datetime
import io

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def calculate_minutes(start_str, end_str):
    try:
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()
        
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        
        if end_minutes < start_minutes:
            return (24 * 60 - start_minutes) + end_minutes
        else:
            return end_minutes - start_minutes
    except:
        return 0

def timecounter(business_id, hours):
    if not hours:
        return (business_id, 0)
    
    total_minutes = 0
    
    for day_schedule in hours.values():
        if not day_schedule or day_schedule == "0:0-0:0":
            continue
            
        try:
            open_time, close_time = day_schedule.split("-")
            open_time = open_time.strip()
            close_time = close_time.strip()
            
            minutes = calculate_minutes(open_time, close_time)
            total_minutes += minutes
        except:
            continue
    
    return (business_id, total_minutes)

for line in input_stream:
    line = line.strip()
    if not line:
        continue
    try:
        business = json.loads(line)
        business_id = business.get("business_id")
        hours = business.get("hours", {})
        
        if not business_id:
            continue
            
        business_id, minutes = timecounter(business_id, hours)
        print(f"{minutes:010d}\t{business_id}\t{minutes}", file=output_stream)
        
    except Exception as e:
        continue
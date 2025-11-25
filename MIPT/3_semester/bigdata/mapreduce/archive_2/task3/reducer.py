#!/usr/bin/env python3

import sys
import io
from heapq import nlargest

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

current_user = None
useful_scores = []
friend_count = 0

for line in input_stream:
    try:
        user_id, data_type, value = line.strip().split('\t')
        
        if user_id != current_user:
            if current_user is not None:
                top5_sum = sum(nlargest(5, useful_scores)) if useful_scores else 0
                print(f"{current_user}\t{top5_sum}\t{friend_count}")
            
            current_user = user_id
            useful_scores = []
            friend_count = 0
        
        if data_type == 'review':
            useful_scores.append(int(value))
        elif data_type == 'user':
            friend_count = int(value)
            
    except:
        continue
    
# последний юзер
if current_user is not None:
    top5_sum = sum(nlargest(5, useful_scores)) if useful_scores else 0
    print(f"{current_user}\t{top5_sum}\t{friend_count}")
#!/usr/bin/env python3

import sys
import json
import io

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

for line in input_stream:
    try:
        obj = json.loads(line.strip())
        
        # Process reviews
        if 'review_id' in obj:
            user_id = obj['user_id']
            useful = obj.get('useful', 0)
            # Emit with prefix for grouping
            print(f"{user_id}\treview\t{useful}")
            
        # Process users
        elif 'user_id' in obj and 'friends' in obj:
            user_id = obj['user_id']
            friends = obj.get('friends', '')
            if friends and friends != 'None':
                friend_count = len([f for f in friends.split(',') if f.strip()])
            else:
                friend_count = 0
            print(f"{user_id}\tuser\t{friend_count}")
            
    except Exception as e:
        continue
#!/usr/bin/env python3

import sys
import json
from datetime import datetime
import io

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
stderr_stream = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


for line in input_stream:
    try:
        obj = json.loads(line)

        # Отзыв
        if 'review_id' in obj:
            user_id = obj['user_id']
            useful = obj.get('useful', 0)
            print(f"{user_id}\tR\t{useful}")

        # Профиль пользователя
        elif 'user_id' in obj and 'friends' in obj:
            user_id = obj['user_id']
            friends_str = obj.get('friends', "")
            if friends_str == "None":
                num_friends = 0
            else:
                num_friends = len([fid.strip() for fid in friends_str.split(",") if fid.strip()])
            print(f"{user_id}\tU\t{num_friends}", file=output_stream)

    except:
        continue
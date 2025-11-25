#!/usr/bin/env python3

import sys
import json
from datetime import datetime
import io

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
stderr_stream = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def friends_counter(user_id, friends):
    if not friends or friends == "None":
        return f"{user_id}\t0"
    
    # создадим включение (для очистки от пробелов) списка по разделенным элементам
    # строки friends и почистим от дублей (если есть)
    friend_list = [fid.strip() for fid in friends.split(",") if fid.strip()]
    friends_count = len(set(friend_list))
    return f"{user_id}\t{friends_count}"
    
    
for line in input_stream:
    line = line.strip()
    if not line:
        continue
    try:
        users = json.loads(line)
        user_id = users.get("user_id")
        friends = users.get("friends")

        if user_id is None:
            continue

        result = friends_counter(user_id, friends)
        print(result, file=output_stream)

    except Exception:
        continue
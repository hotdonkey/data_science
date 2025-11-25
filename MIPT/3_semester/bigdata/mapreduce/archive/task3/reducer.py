#!/usr/bin/env python3

import sys
import io
from heapq import nlargest

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
stderr_stream = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


current_user = None
useful_list = []
num_friends = 0
has_reviews = False
has_friends = False

def emit(user, useful_sum, friends):
    print(f"{user}\t{useful_sum}\t{friends}")

for line in input_stream:
    try:
        parts = line.strip().split('\t')
        if len(parts) != 3:
            continue
        user_id, tag, value = parts

        if user_id != current_user:
            # Выводим предыдущего пользователя, если есть и отзывы, и друзья
            if current_user and has_reviews and has_friends:
                top5_sum = sum(nlargest(5, useful_list))
                emit(current_user, top5_sum, num_friends)
            # Сбрасываем состояние
            current_user = user_id
            useful_list = []
            num_friends = 0
            has_reviews = False
            has_friends = False

        if tag == 'R':
            useful_list.append(int(value))
            has_reviews = True
        elif tag == 'U':
            num_friends = int(value)
            has_friends = True

    except:
        continue

# Последний пользователь
if current_user and has_reviews and has_friends:
    top5_sum = sum(nlargest(5, useful_list))
    emit(current_user, top5_sum, num_friends)
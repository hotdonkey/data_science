#!/usr/bin/env python3
import sys
import json
from pyspark import SparkContext

output_path = sys.argv[1]
sc = SparkContext(appName="Influencers")

def count_func():
    # Отзывы и их предобработка
    reviews_rdd = sc.textFile("/data/yelp/review_sample")
    
    def parse_review(line):
        obj = json.loads(line)
        return (obj['user_id'], obj.get('useful', 0))

    # Топ 5 юзеров по полезности
    top5_useful_rdd = (
        reviews_rdd.map(parse_review)
        .groupByKey()
        .mapValues(lambda vals: sum(sorted(vals, reverse=True)[:5]))
        .filter(lambda x: x[1] > 0)
    )

    # Пользователи и их предобработка
    users_rdd = sc.textFile("/data/yelp/user_sample")
    
    def parse_user(line):
        obj = json.loads(line)
        user_id = obj['user_id']
        friends_str = obj.get('friends', '')
        if friends_str and friends_str != 'None':
            friends = [f.strip() for f in friends_str.split(',') if f.strip()]
        else:
            friends = []
        return (user_id, friends)

    # RDD по друзьям
    user_friends_rdd = users_rdd.map(parse_user)
    user_friends_dict = dict(user_friends_rdd.collect())

    # Расчет друзей-друзей, система не пропускала очищенный граф,
    # а хотела видеть и дублирующие записи судя по-всему
    def compute_fof(user_id, friends_list, all_users_dict):
        fof_count = 0
        for friend in friends_list:
            if friend in all_users_dict:
                fof_count += len(all_users_dict[friend])  # все друзья друга
        return fof_count

    # RDD для друзей-друзей
    fof_rdd = user_friends_rdd.map(
        lambda x: (x[0], compute_fof(x[0], x[1], user_friends_dict))
    )

    # Джойн и сортировка
    joined_rdd = top5_useful_rdd.join(fof_rdd)
    scored_rdd = joined_rdd.map(
        lambda x: (x[0], x[1][0], x[1][1], x[1][0] * x[1][1])
    )

    # Топ 10
    top10 = (
        scored_rdd
        .sortBy(lambda x: x[3], ascending=False)
        .map(lambda x: (x[0], x[1], x[2]))
        .take(10)
    )

    # Результирующая RDD
    result_rdd = sc.parallelize(top10).map(
        lambda x: f"{x[0]}\t{x[1]}\t{x[2]}"
    )

    # Сохраняем все
    result_rdd.saveAsTextFile(output_path)

    # Выводим
    top10 = result_rdd.take(10)
    for i in top10:
        print(i)

def main():
    try:
        count_func()
    
    finally:
        sc.stop()
    
if __name__ == "__main__":
    main()

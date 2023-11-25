"""reducer.py"""

from operator import itemgetter
import sys

current_word = None
current_count = 0
word = None

# Ввод берется из стандартного ввода для myline в sys.stdin:
for line in sys.stdin:
    # удалим пробелы по сторонам
    myline = line.strip()

    # Разделим ввод, который мы получили из mapper.py на слово и счетчик
    word, count = line.split('\t', 1)

    # проверяем, является ли count числом
    try:
        count = int(count)
    except ValueError:
        # Count не было числом, поэтому будем игнорировать эту строку.
        pass

    if current_word == word:
        current_count += count
    else:
        if current_word:
            # Выводим слово
            print('%s\t%s' % (current_word, current_count))

        current_count = count
        current_word = word

# Не забываем вывести последнее слово, если нужно!
if current_word == word:
    print('%s\t%s' % (current_word, current_count))


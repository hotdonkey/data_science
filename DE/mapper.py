"""mapper.py"""

import sys

# Ввод берется из стандартного ввода в sys.stdin:
for line in sys.stdin:
    # удалим пробелы с обеих сторон
    myline = line.strip()

    # разобьем текст на слова
    words = myline.split()

    # выведем все слова с новой строки, через табуляцию с единицей
    for myword in words:
        # выведем результат
        print('%s\t%s' % (myword, 1))

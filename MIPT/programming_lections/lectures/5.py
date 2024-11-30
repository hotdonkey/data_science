import math
import time


def read_data():
    data = open('C:\\PrivateRepos\\MFTI\\Python1\\war_peace_processed.txt', 'rt', -1, 'utf8').read()
    return data.split('\n')


def get_document_frequency(words, target_word, chapter_sep):
    number_of_documents = 1
    number_of_documents_with_target_word = 0
    skip_chapter = False

    for word in words:
        if word == chapter_sep:
            number_of_documents += 1
            skip_chapter = False
        elif not skip_chapter and word == target_word:
            number_of_documents_with_target_word += 1
            skip_chapter = True

    return number_of_documents_with_target_word / number_of_documents


def get_term_frequency(words, target_word, target_chapter, chapter_sep):
    total_words_in_chapter_count = 0
    target_words_in_chapter_count = 0
    current_chapter = 0

    for word in words:
        if word == chapter_sep:
            current_chapter += 1
            continue

        if current_chapter == target_chapter:
            total_words_in_chapter_count += 1
            if word == target_word:
                target_words_in_chapter_count += 1
        elif current_chapter > target_chapter:
            break

    return target_words_in_chapter_count / total_words_in_chapter_count


def get_word_contrast(words, target_word, target_chapter, chapter_sep):
    df = get_document_frequency(words, target_word, chapter_sep)
    idf = 1 / df
    tf = get_term_frequency(words, target_word, target_chapter, chapter_sep)
    return math.log(1 + tf) * math.log(idf)


def get_chapter_words(words, target_chapter, chapter_sep):
    chapter_words = []
    current_chapter = 0
    for word in words:
        if word == chapter_sep:
            current_chapter += 1
            continue

        if current_chapter == target_chapter:
            chapter_words.append(word)
        elif current_chapter > target_chapter:
            break

    return chapter_words


chapter_sep = '[new chapter]'
target_chapter = 4
most_contrasting_words_count = 3
words = read_data()
contrasting_word_dict = {}

start = time.perf_counter()

for word in get_chapter_words(words, target_chapter, chapter_sep):
    if not contrasting_word_dict.get(word):
        contrasting_word_dict[word] = get_word_contrast(words, word, target_chapter, chapter_sep)

sorted_word_values = sorted(contrasting_word_dict.items(), key=lambda x: x[1], reverse=True)
sorted_words = list(map(lambda x: x[0], sorted_word_values))
print(' '.join(sorted_words[:most_contrasting_words_count]))

finish = time.perf_counter()
print('Время работы: ' + str(finish - start))

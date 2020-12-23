num_words = int(input())
arr_words = []
for i in range(num_words):
    arr_words.append((input()).lower())

num_words_for_check = int(input())
uniq_errors = []
for i in range(num_words_for_check):
    words = (input()).split(' ')
    for word in words:
        lower = word.lower()
        if lower not in arr_words and lower not in uniq_errors:
            uniq_errors.append(lower)

for el in uniq_errors:
    print(el)


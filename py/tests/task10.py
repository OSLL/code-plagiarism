import wikipedia


def is_page_valid(page):
    try:
        wikipedia.page(page)
    except Exception:
        return False
    return True


def is_right_lang(lang):
    return lang in wikipedia.languages()


def cnt_word(string):
    return len(string.replace('\n', ' ').replace('\t', ' ').split(' '))


def max_cnt_words_summary(page_array):
    maxCnt = 0
    ansPage = ""
    for page in page_array:
        cntInStr = cnt_word(wikipedia.page(page).summary)
        if cntInStr >= maxCnt:
            maxCnt = cntInStr
            ansPage = page
    return [maxCnt, wikipedia.page(ansPage).title]


def find_support_chain(page_array, links_array, i):
    for item in links_array:
        if not is_page_valid(item):
            continue
        if page_array[i + 1] in wikipedia.page(item).links:
            return item


def find_chain(page_array):
    answerArray = [page_array[0]]
    for i in range(0, len(page_array) - 1):
        linksArray = wikipedia.page(page_array[i]).links
        if page_array[i + 1] not in linksArray:
            answerArray.append(find_support_chain(page_array, linksArray, i))
        answerArray.append(page_array[i + 1])
    return answerArray


array = input().split(', ')
if is_right_lang(array[-1]):
    wikipedia.set_lang(array.pop())
else:
    print("no results")
    quit(0)
print(*max_cnt_words_summary(array))
print(find_chain(array))      
  

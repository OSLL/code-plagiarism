import wikipedia


def is_page_valid(page):
    try:
        wikipedia.page(page)
    except Exception:
        return False
    return True


def chek(language):
    if language in wikipedia.languages():
        wikipedia.set_lang(language)
    else:
        print('no results')
        exit(0)


def search_maximum(pages):
    outline = [wikipedia.summary(i) for i in pages]
    maximum_word = [len(i.split()) for i in outline]
    maxim_word = maximum_word[::-1]
    maxim = maxim_word.index(max(maximum_word))
    print(maximum_word[len(maximum_word) - 1 - maxim],
          wikipedia.page(pages[len(maximum_word) - 1 - maxim]).title)
    return 0


def chain(pages):
    answer = [pages[0]]
    for i in range(1, len(pages)):
        tag = wikipedia.page(answer[-1]).links
        if pages[i] in tag:
            answer.append(pages[i])
        else:
            for item in tag:
                if is_page_valid(item):
                    if pages[i] in wikipedia.page(item).links:
                        answer.append(item)
                        break
            answer.append(pages[i])
    return answer


input_string = input()
list_input = input_string.split(', ')
chek(list_input[-1])
search_maximum(list_input[:-1])
answer = chain(list_input[:-1])
print(answer)      
  

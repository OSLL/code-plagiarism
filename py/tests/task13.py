import wikipedia


def is_page_valid(page):
    try:
        wikipedia.page(page)
    except Exception:
        return False
    return True


def setting_of_language(lang):
    if lang in wikipedia.languages():
        wikipedia.set_lang(lang)
    else:
        return 'no results'


def maximum_words(pages):
    maximum = -1
    name_page = ''
    for name in pages:
        p = wikipedia.page(name)
        if len(p.summary.split()) >= maximum:
            maximum = len(p.summary.split())
            name_page = p.title
    result = str(maximum) + ' ' + name_page
    return result


def find_intermediate(page_one, page_two):
    for name in page_one.links:
        if is_page_valid(name):
            p_intermediate = wikipedia.page(name)  
            if page_two.title in p_intermediate.links:
                return name


def task_3(pages):
    result = [pages[0]]
    for i in range(len(pages) - 1):
        p1 = wikipedia.page(pages[i])
        p2 = wikipedia.page(pages[i+1])
        if pages[i+1] in p1.links:
            result.append(pages[i+1])
        else:
            result.append(find_intermediate(p1, p2))  
    return result


data = [x.strip() for x in input().split(',')]
language = data[-1]
data = data[:-1]

if setting_of_language(language) != 'no results':
    print(maximum_words(data))
    print(task_3(data))
else:
    print(setting_of_language(language)) 

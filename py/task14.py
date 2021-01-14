import wikipedia


def is_page_valid(page):
    try:
        wikipedia.page(page)
    except Exception:
        return False
    return True


def max_word_number(pagel):
    max_word = 0
    title = ""
    for page in pagel:
        if len(wikipedia.page(page).summary.split()) >= max_word:
            max_word = len(wikipedia.page(page).summary.split())
            title = wikipedia.page(page).title
    return max_word, title


def pagel_link(page1, page2):
    for page in page1.links:
        if is_page_valid(page):
            page_link = wikipedia.page(page)
            if page2.title in page_link.links:
                return page


def pagel_chains(pagel):
    pagel_chain = [pagel[0]]
    for item in range(len(pagel) - 1):
        page1 = wikipedia.page(pagel[item])
        page2 = wikipedia.page(pagel[item + 1])
        if pagel[item + 1] in page1.links:
            pagel_chain.append(pagel[item + 1])
        else:
            pagel_chain.append(pagel_link(page1, page2))
            pagel_chain.append(pagel[item + 1])
    return pagel_chain


pagel = input().split(", ")
if wikipedia.languages().get(pagel[-1]) is None:
    print("no results")
else:
    wikipedia.set_lang(pagel[-1])
    print(max_word_number(pagel[:-1])[0], max_word_number(pagel[:-1])[1])
    print(pagel_chains(pagel[:-1])) 

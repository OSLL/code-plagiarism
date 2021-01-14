import wikipedia

def is_page_valid(page):
    try:
        wikipedia.page(page)
    except Exception:
        return False
    return True

def max_words_title(pages):
    max_count = 0
    title = None
    for page_name in pages:
        if is_page_valid(page_name):
            page_obj = wikipedia.page(page_name)
            words_count = len(page_obj.summary.split())
            if words_count > max_count:
                max_count = words_count
                title = page_obj.title
    return max_count, title

def shortest_chain(pages):
    chain = [pages[0]]
    for i in range(1, len(pages)):
        if is_page_valid(pages[i - 1]):
            links = wikipedia.page(pages[i - 1]).links
            if pages[i] in links:
                chain.append(pages[i])
            else:
                j = 0
                while pages[i] not in wikipedia.page(links[j]).links:
                    j += 1
                chain.extend([links[j], pages[i]])
    return chain

def main():
    pages = input().split(", ")
    lang = pages.pop(-1)
    all_langs = wikipedia.languages()
    if lang in all_langs:
        wikipedia.set_lang(lang)
        print(*max_words_title(pages))
        print(shortest_chain(pages))
    else:
        print("no results")

if __name__ == '__main__':
    main()      

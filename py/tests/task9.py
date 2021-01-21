import wikipedia


def is_page_valid(page):
    try:
        wikipedia.page(page)
    except Exception:
        return False
    return True


def get_max_summary(inp):
    max_summ = 0
    max_name = ''
    for i in inp:
        len_summ = len(i.summary.split())
        if len_summ >= max_summ:
            max_summ = len_summ
            max_name = i.title
    return max_summ, max_name


def get_wiki_chain(inp_title, inp):
    chain_list = [inp_title[0]]
    chain_pages = [inp[0]]
    for i in range(1, len(inp)):
        if inp_title[i] not in chain_pages[len(chain_pages) - 1].links:
            flag = 1
            for j in chain_pages[len(chain_pages) - 1].links:
                if flag:
                    if is_page_valid(j):
                        if inp[i].title in wikipedia.page(j).links:
                            chain_list.append(j)
                            flag = 0
        chain_list.append(inp_title[i])
        chain_pages.append(inp[i])
    return chain_list


wiki_list = input().split(', ')
if wiki_list[len(wiki_list) - 1] not in wikipedia.languages():
    print("no results")
else:
    wikipedia.set_lang(wiki_list[len(wiki_list) - 1])
    wiki_titles = wiki_list[:-1]
    wiki_list = [wikipedia.page(wiki_list[i]) for i in range(len(wiki_titles))]
    wiki_max = get_max_summary(wiki_list)
    print(wiki_max[0], wiki_max[1])
    wiki_chain = get_wiki_chain(wiki_titles, wiki_list)
    print(wiki_chain)      
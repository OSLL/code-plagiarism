import wikipedia
def lang(lan):
    if lan in wikipedia.languages():
        wikipedia.set_lang(lan)
        return True
    else:
        return False
def is_page_valid(page):
    try:
        wikipedia.page(page)
    except Exception:
        return False
    return True
def max_words(names):
    count=0
    name=""
    for i in names:
        if is_page_valid(i):
            page=wikipedia.page(i)
            if len(page.summary.split()) >= count:
                count=len(page.summary.split())
                name=page.title
    return count,name

def list_chain(names):
    for i in range(len(names)-1):
        links_i=wikipedia.page(names[i]).links
        if names[i+1] in links_i:
            list.append(names[i+1])
        else:
            for j in links_i:
                if is_page_valid(j):
                    links_j=wikipedia.page(j).links
                    if names[i+1] in links_j:
                        list.append(j)
                        list.append(names[i+1])
                        break
def all_page_valid(names):
    for i in names:
        if is_page_valid(i) == 0:
            return False
    return True

names=input().split(', ')
lg=names[-1]
names=names[:len(names)-1]
list=[names[0]]
if lang(lg) and all_page_valid(names):
    max=max_words(names)
    max_count=max[0]
    name_max=max[1]
    list_chain(names)
    print(max_count,name_max)
    print(list)
else:
    print ("no results")

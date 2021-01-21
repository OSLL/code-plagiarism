import wikipedia

def check_lang(lang):
    if lang in wikipedia.languages().keys():
        wikipedia.set_lang(lang)
        return True
    return False


def find_longest(pages):
    max_words = 0
    max_name = ''
    for page in pages:
        wcount = len(page.summary.split())  
        if wcount >= max_words:
            max_words = wcount
            max_name = page.title
    return max_words, max_name


def page_chain(pages, raw_names):
    answer = [raw_names[0]]
    for i in range(len(pages)-1):
        ls = pages[i].links
        if raw_names[i+1] not in ls:            
            for j in range(len(ls)):           
                if raw_names[i+1] in wikipedia.page(ls[j]).links:   
                    answer.append(ls[j])       
                    break               
        answer.append(raw_names[i+1])
    return answer


# main
if __name__ == '__main__':
    inp = input().split(', ')
    lang = inp.pop()
    if len(inp) < 1 or not check_lang(lang):
        print("no results")
        exit()
    pages = [wikipedia.page(i) for i in inp]
    max_words, max_name = find_longest(pages)
    chain = page_chain(pages, inp)
    print(max_words, max_name)
    print(chain) 

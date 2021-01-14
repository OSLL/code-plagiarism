import wikipedia as wiki
import sys

data = input().split(', ')
titles = data[:-1]
lang = data[-1]

# subtask 1
if lang not in wiki.languages():
    print('no results')
    sys.exit(0)

wiki.set_lang(lang)

pages = [wiki.page(i) for i in titles]

# subtask 2
lp = max(pages[::-1], key=lambda x: len(x.summary.split()))
print(len(lp.summary.split()), lp.title)

# subtask 3
chain = [titles[0]]
for i in range(len(pages) - 1):
    if titles[i + 1] not in pages[i].links:
        for j in pages[i].links:
            if pages[i + 1].title in wiki.page(j).links:
                chain.append(j)
                break  # break cycle because guaranteed 1 or 0 intermediate pages
                
    chain.append(titles[i + 1])

print(chain) 
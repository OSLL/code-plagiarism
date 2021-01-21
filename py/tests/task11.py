import wikipedia

a = input().split(', ')
b = a[0:len(a)-1]
if a[len(a)-1] in wikipedia.languages():
    wikipedia.set_lang(a[len(a)-1])
else:
    print('no results')

def is_page_valid(page):
    try:
        wikipedia.page(page)
    except Exception:
        return False
    return True

def spisoksslk(b1, b2):
    spage1 = wikipedia.page(b1)
    #print(b1)
    rez = []
    #print("ffff")
    sslk = spage1.links
    if b2 in sslk:
        #print(wikipedia.page(b2).links)
        rez.append(b2)
    else:
        #print('ELSE')
        for i in sslk:
            #print(wikipedia.page(b2).links)
            #print('FOR')
            if is_page_valid(i):
                #print('VALID')
                #spage3 = wikipedia.page(i)
                #sslk3 = spage3.links
                #print(sslk3)
                if b2 in wikipedia.page(i).links:
                    #print(wikipedia.page(b2).links)
                    #print(i, b2)
                    rez.append(i)
                    rez.append(b2)
                    break
    #print(rez)
    return(rez)

max = 0

kol = 0
rez = 0
for i in a:
    t = wikipedia.page(i)
    if kol <= len(t.summary.split()):
        kol = len(t.summary.split())
        rez = wikipedia.page(i).title
print(kol, rez)

result = []
result.append(b[0])

for sp in range(len(b)-1):
    new = spisoksslk(b[sp], b[sp+1])
    #print(new)
    #if new == []:
    #    #print('break')
    #    break
    #else:
    for k in new:
        result.append(k)

print(result)


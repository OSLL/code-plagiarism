import wikipedia

def maxwords (titles):
  max = 0
  maxname = ''
  for i in titles:
    if max < len(wikipedia.page(i).summary.split()):
      max = len(wikipedia.page(i).summary.split())
      maxname = wikipedia.page(i).title
  return str(max)+' '+maxname

def way(titles):
  answ = [titles[0]]
  for i in range(len(titles)-1):
    #print(wikipedia.page(titles[i]).links)
    if titles[i+1] in wikipedia.page(titles[i]).links:
      answ.append(titles[i+1])
    else:
      for j in wikipedia.page(titles[i]).links:
        if titles[i+1] in wikipedia.page(j).links:
          answ.append(j)
          answ.append(titles[i+1])
          break
  return answ

titles = input().split(', ')
language = titles.pop(-1)
if language in wikipedia.languages():
  wikipedia.set_lang(language)
  print (maxwords(titles))
  print (way(titles))
else:
  print("no results")

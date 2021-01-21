import wikipedia

def is_page_valid(page):
    try:
        wikipedia.page(page)
    except Exception:
        return False
    return True

def max_page_summary(list_input):
  max_page = ''
  max = 0
  for i in range(0, len(list_input)):
    if max <= len(wikipedia.page(list_input[i]).summary.split()):
      max_page = wikipedia.page(list_input[i]).title
      max = len(wikipedia.page(list_input[i]).summary.split())
  return max_page, max

def chain_links(list_input):
  result = []
  result.append(list_input[0])
  for i in range(0, len(list_input) - 1):
    list_links = wikipedia.page(list_input[i]).links
    if list_input[i + 1] in list_links:
      result.append(list_input[i + 1])
    else:
      for link in list_links:
        if is_page_valid(link):
          list_links_next = wikipedia.page(link).links
          if (list_input[i + 1] in list_links_next):
            result.append(list_links[list_links.index(link)])
            result.append(list_input[i + 1])
            break
          else:
            continue
        else:
          continue
  return result

list_input = input().split(', ')
if list_input[-1] in wikipedia.languages():
  wikipedia.set_lang(list_input[-1])
  list_input.pop(-1)
  print(max_page_summary(list_input)[1], max_page_summary(list_input)[0])
  print(chain_links(list_input))
else:
  print('no results') 

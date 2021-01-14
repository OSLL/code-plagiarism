import wikipedia as wiki 

def main():
	pages = input().split(', ')
	lang = pages.pop()
	if lang in wiki.languages(): wiki.set_lang(lang)
	else:
		print('no results')
		return

	max_sum = max_summary(pages)
	print(max_sum[0], max_sum[1]) 
	print(get_path(pages))


def is_page_valid(page):
	try: wiki.page(page)
	except Exception: return False
	return True


def max_summary(pages):
	maximum = [0, '']
	for page in pages:
		page_summary = len(wiki.summary(page).split())
		if page_summary >= maximum[0]:
			maximum[0], maximum[1] = page_summary, wiki.page(page).title
	return maximum


def get_path(pages):
	path = [pages[0]]
	for i in range(1, len(pages)):
		links = wiki.page(path[-1]).links
		if pages[i] in links:
			path.append(pages[i])
		else:
			for link in links:
				if is_page_valid(link) and pages[i] in wiki.page(link).links:
					path.append(link)
					break
			path.append(pages[i])
	return path

main()  

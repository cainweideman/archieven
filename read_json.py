import json

def get_json(path_to_json):
	f = open(path_to_json, 'r')
	data = json.load(f)
	f.close()

	return data

def get_text(data, first_page, last_page):
	first_page_index = first_page -1
	last_page_index = last_page
	text_list = []

	for i in data['content'][first_page_index:last_page_index]:
		text = i['text']
		text_list.append(text)
	
	#return ''.join(text_list)
	return text_list


path_to_json = 'data/1854/text/1854.json'
data = get_json(path_to_json)

#text = get_text(data, first_page=7, last_page=102)
text_list = get_text(data, first_page=7, last_page=102)

for i in text_list:
	print(repr(i))
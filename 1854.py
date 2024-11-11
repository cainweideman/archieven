import json
import re

def open_json(path_to_json):
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

	return ''.join(text_list)

def strip_text(text):
  regex = re.compile("[^a-zA-Z0-9\s,.\n']")
  text = regex.sub('', text)

  return text

def get_job_list(text_list):
  job_list = []
  for line in text_list:
    if line.isupper() and len(line) > 3:
      job_list.append(line)

  return job_list

def extract_lines(text):
	text_list = text.replace('\n\n', '\n').split('\n')
	job_list = get_job_list(text_list)
	index_list = []
	job_dict = {}

	for job in job_list:
		index = text_list.index(job)
		index_list.append(index)

	for index, i in enumerate(index_list):
		first_index = i
		if i == index_list[-1]:
			last_index = len(text_list)
		else:
			last_index = index_list[index+1]
		job_dict[text_list[first_index]] = text_list[first_index + 1 : last_index]

	return job_dict # Dictionary where key is jobname and value is all lines of text between the jobname and the next jobname

def add_spaces(sentence):
  sentence = re.sub(r'(?<=[.])(?=[^\s])', r' ', sentence)
  sentence = re.sub(r'\s+', ' ', sentence)
  return sentence

def find_preposition(name_list, address_list):
  name_list = name_list
  address_list = address_list
  address_list = [item.replace(',', '') for item in address_list]

  if 'van' in address_list:
    name_list.append('van')
    address_list.remove('van')
  if 'de' in address_list:
    name_list.append('de')
    address_list.remove('de')
  if 'der' in address_list:
    name_list.append('der')
    address_list.remove('der')
  if 'den' in address_list:
    name_list.append('den')
    address_list.remove('den')
  if 'ter' in address_list:
    name_list.append('ter')
    address_list.remove('ter')
  if 'ten' in address_list:
    name_list.append('ten')
    address_list.remove('ten')
  if 'vander' in address_list:
    name_list.append('vander')
    address_list.remove('vander')

  return name_list, address_list

def count_initials(sentence):
  sentence = add_spaces(sentence)
  parts = sentence.split()

  initials_pattern = re.compile(r'^[A-Za-z](?:[.,])$')

  initials = []

  # Loop through the parts and find all initials
  for part in parts:
      part = part.strip()
      # Check if the part matches the initials pattern
      if initials_pattern.match(part):
          initials.append(part)

  # Count the number of initials
  num_initials = len(initials)

  # Determine the final initial
  if num_initials > 0:
      # If the last initial contains 'n' or 'o', consider the second last initial
      if 'n' in initials[-1].lower() or 'o' in initials[-1].lower():
          final_initial = initials[-2] if num_initials > 1 else initials[-1]
      else:
          final_initial = initials[-1]
  else:
      final_initial = None

  # Find the position of the final initial in the sentence
  final_initial_position = -1
  if final_initial:
      final_initial_position = parts.index(final_initial)

  name = parts[:final_initial_position + 1]
  address = parts[final_initial_position+1:]
  name_list, address_list = find_preposition(name, address)

  return name_list, address_list

def format_name(name_list):
  initials_pattern = re.compile(r'^[A-Za-z](?:[.,])$')

  initials = []
  prepositions = ['van', 'de', 'der', 'den', 'ter', 'ten', 'vander']

  # Loop through the parts and find all initials
  for item in name_list:
    item = item.strip()
    # Check if the part matches the initials pattern
    if not initials_pattern.match(item):
      name_list.remove(item)
      name_list.append(item)
    else:
      break

  # Count the number of initials
  name = ' '.join(name_list).rstrip(',')
  name = name.replace(',', '.')
  return name
  #return " ".join(name_list).rstrip(',')

def make_json_object(name, job, address):
	person = {
				'@context': 'https://schema.org',
				'@type': 'Person'
			}
    
	person['name'] = name
	person['address'] = address
	person['jobTitle'] = job
    
	return person

def extract_people(job_dict):
  for key, value in job_dict.items():
    job = key
    lines = value
    for line in lines:
      name, address = count_initials(line)
      if len(name) > 1 and address:
        for item in address:
          if any(chr.isdigit() for chr in item):
            #print(f'Name: {format_name(name)}\nAddress: {" ".join(address)}\nJob: {job}\n')
            complete_name = format_name(name)
            job = job[0] + job[1:].lower().rstrip('.')
            address = ' '.join(address).rstrip('.')
            print(make_json_object(complete_name, job, address))

path_to_json = 'data/1854/text/1854.json'
data = open_json(path_to_json)

text = get_text(data, first_page=7, last_page=102)
text = strip_text(text)
job_dict = extract_lines(text)

extract_people(job_dict)
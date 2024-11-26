import json
import re
from tqdm import tqdm


def load_json(path_to_json):
	"""
	Opens a JSON file and returns its content as a dictionary.

	Args:
		path_to_json (str): The path to the JSON file.

	Returns:
		dict: Parsed JSON data.
	"""
	try:
		with open(path_to_json, 'r') as f:
			data = json.load(f)
		return data
	except (FileNotFoundError, json.JSONDecodeError) as e:
		print(f"Error loading JSON file: {e}")
		return None


def get_text(data, first_page, last_page):
	"""
	Extracts text content from specified pages in the JSON data.

	Args:
		data (dict): JSON data containing the content.
		first_page (int): Starting page number (inclusive).
		last_page (int): Ending page number (inclusive).

	Returns:
		list: Text from the specified pages.
    """
	first_page_index = first_page -1
	last_page_index = last_page
	text_list = []

	for page in data['content'][first_page_index:last_page_index]:
		text = page['text'].replace('-\n', '')
		text_list.append(text)

	return text_list


def check_for_person(sentence):
    if '(' in sentence or ')' in sentence:
        return True
    else:
        return False


def make_person(name, job, address):
    """
    Creates a JSON object for a person.

    Args:
        name (str): Full name of the person.
        job (str): Job title.
        address (str): Address.

    Returns:
        dict: JSON object representing the person.
    """
    return {
        '@context': 'https://schema.org',
        '@type': 'Person',
        'name': name,
        'address': address,
        'jobTitle': job
    }


def remove_junk(line_list):
	new_line_list = []
	for line in line_list:
		if check_for_person(line) or any(char.isdigit() for char in line):
			new_line_list.append(line)
	
	return new_line_list


def dot_initials(string):
	return re.sub(r'(?<=[A-Z])(?!\.)\b', '.', add_spaces(string))


def add_spaces(sentence):
    """
    Adds spaces after periods if missing.

    Args:
        sentence (str): The input sentence.

    Returns:
        str: Formatted sentence with proper spacing.
    """
    sentence = re.sub(r'(?<=[.])(?=[^\s])', r' ', sentence)
    sentence = re.sub(r'\s+', ' ', sentence)
    
    return sentence


def strip_text(text):
	"""
	Removes special characters, keeping only alphanumeric characters, spaces, commas, periods, and newlines.

	Args:
		text (str): The input text.

	Returns:
		str: Cleaned text.
	"""
	regex = re.compile("[^a-zA-Z0-9\s,.\n']")
	return regex.sub('', text)


def find_item_with_digit(input_list):
    """
    Finds the first item in the list that contains a digit.
    If no such item exists, returns an empty list.
    
    :param input_list: List of strings
    :return: First string containing a digit or an empty list
    """
    for item in input_list:
        if any(char.isdigit() for char in item):
            return item
    return []


def find_prefixes(name):
	#return re.findall(r'\b([vd]\.?[a-z]{0,2})\b', name)
	#return re.findall(r'(?<!\S)[vdt]\.?[a-z]{0,2}', name)
	return re.findall(r'(?:(?<=\s)|(?<=^)|(?<=\.))[vd]\.?[a-z]{0,2}', name)


def find_initials(name):
	return re.findall(r'\b[A-Z]\.', name)


def find_name(person):
	name = person['name']
	name = strip_text(name)
	name = dot_initials(name)
	#print(name)
	initials = find_initials(name)
	prefixes = find_prefixes(name)
	if prefixes:
		index = name.rfind(prefixes[-1])
		length = len(prefixes[-1])
		full_name = name[:index+length]
		rest = name[index+length:]
		return full_name, rest
	elif initials:
		index = name.rfind(initials[-1])
		length = len(initials[-1])
		full_name = name[:index+length]
		rest = name[index+length:]
		return full_name, rest
	else:
		full_name = name
		rest = ''
	
	return full_name, rest



def post_process_person(person):
	name = person['name']
	job = person['jobTitle']

	if not isinstance(person['address'], list):
		person['address'] = [person['address']]

	person['address'] = [part for part in person['address'] if part]
	address = person['address']

	if len(address) > 1:
		if ')' in job:
			person['name'] = name + job
			if len(address) > 1:
				person['jobTitle'] = address[0]
				person['address'] = address[1:]
			else:
				person['jobTitle'] = 'None'

	elif not address and any(char.isdigit() for char in person['jobTitle']):
		person['address'] = person['jobTitle']
		person['jobTitle'] = 'None'

	if not isinstance(person['address'], list):
		person['address'] = [person['address']]

	address1 = person['address']
	person['address'] = [part for part in person['address'] if any(char.isdigit() for char in part)]
	if len(person['address']) >= 1:
		person['address'] = person['address'][0]

	if not person['address']:
		old_address = "".join(address1)
		if len(old_address) > 5:
			person['address'] = old_address
		#print(person)


	if any(char.isdigit() for char in person['jobTitle']) and person['address']:
		temp_address = person['address']
		#re.sub(r'[0-9\s]', '', temp_address)
		temp_address = re.sub(r"[^a-zA-Z.,()\-'\" ]", '', temp_address)
		if len(temp_address) < 5:
			person['address'] = person['jobTitle']
			person['jobTitle'] = 'None'

	full_name, rest = find_name(person)
	#print(f'name: {full_name} -> rest: {rest}')
	rest = rest.strip('.')
	if rest != '':
		regex = re.compile("[^a-zA-Z]")
		address = person['address']
		if not person['address']:
			address = ''
		else:
			address = regex.sub('', person['address'])

		if address == '' or address[0].islower():
			print(f'address found: {rest}')
		elif person['jobTitle'] == 'None' and not any(char.isdigit() for char in rest):
			print(f'job found: {rest}')

	return person


def process_sentences(sentences):
	# Processed list to store combined sentences
	processed_sentences = []
	current_sentence = ""  # To build the current sentence group

	for i, sentence in enumerate(sentences):
		# Check if the current sentence has '(' or ')'
		if '(' in sentence or ')' in sentence:
			# If there's a current combined sentence, add it to the list
			if current_sentence:
				processed_sentences.append(current_sentence.strip())
			
			# Start a new sentence group with the current sentence
			current_sentence = sentence
		else:
			# Append sentence without parentheses to the current sentence group
			current_sentence += " " + sentence

	# Add the last accumulated sentence if any
	if current_sentence:
		processed_sentences.append(current_sentence.strip())
	
	return processed_sentences

year = "1911"
path_to_json = f"book_text/{year}.json"

data = load_json(path_to_json)
first_page, last_page = 107, 414

if data:
	person_list = []
	text_list = get_text(data, first_page, last_page)
	for index, page in tqdm(enumerate(text_list), total=len(text_list), ncols=100, unit='page', desc='Processing Pages'):
		print(f'Page: {first_page + index}')
		text = page.replace('\n\n', '\n')
		line_list = text.split('\n')
		complete_lines = process_sentences(remove_junk(line_list))
		complete_lines = [line.strip() for line in complete_lines]
		for line in complete_lines:
			#print(line)
			parts = line.split(',')
			#print(parts)
			#parts = [part for part in parts if len(parts) > 1]
			#print(parts)
			if len(parts) > 1:
				name = parts[0]
				if len(parts) == 2:
					job = "None"
					address = parts[1]			
				elif len(parts) > 2:
					job = parts[1]
					address = parts[2:]
				person = make_person(name, job, address)
				person = post_process_person(person)
				print(person)
				person_list.append(person)
		print('\n')

	print(f'Amount of people extracted: {len(person_list)}')

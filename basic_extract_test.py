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
	regex = re.compile("[^a-zA-Z0-9\s,.\n'-]")
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


def remove_name_from_job(person):
	name = person['name']
	job = person['jobTitle']

	if '(' in job or ')' in job or '}' in job:
		person['name'] = name + job
		person['jobTitle'] = 'None'
	
	return person


def find_prefixes(name):
	matches = list(re.finditer(r'(?:(?<=\s)|(?<=^)|(?<=\.))[vdt]\.?[a-z]{0,2}', name))
	if matches:
		last_match = matches[-1]  # Get the last match
		start_index = last_match.start() -1  # Start index of the last match
		end_index = last_match.end()  # End index of the last match (inclusive)
		return name[start_index:end_index]
	else:
		return matches  # No match found


def find_initials(name):
	matches = list(re.finditer(r'\b[A-Z]\.', name))
	if matches:
		last_match = matches[-1]  # Get the last match
		start_index = last_match.start() -1  # Start index of the last match
		end_index = last_match.end() # End index of the last match (inclusive)
		return name[start_index:end_index]
	else:
		return matches  # No match found
	

def find_name(person):
	name = person['name']
	name = strip_text(name)
	name = dot_initials(name)

	index_list = []

	initials = find_initials(name)
	if initials:
		final_initial = initials
		final_initial_index = name.rfind(final_initial) + len(final_initial)
		index_list.append(final_initial_index)

	prefixes = find_prefixes(name)
	if prefixes:
		final_prefix = prefixes
		final_prefix_index = name.rfind(final_prefix) + len(final_prefix)
		index_list.append(final_prefix_index)

	if index_list:
		final_index = max(index_list)
		return name[:final_index], name[final_index:]
	else:
		return name, ''
	



year = "1911"
path_to_json = f"book_text/{year}.json"

data = load_json(path_to_json)
first_page, last_page = 107, 414

if data:
	file = open('test.txt', 'w', encoding="utf-8")
	text_list = get_text(data, first_page, last_page)
	for index, page in tqdm(enumerate(text_list), total=len(text_list), ncols=100, unit='page'):
		#print(f'Page: {first_page + index}')
		text = page.replace('\n\n', '\n')
		line_list = text.split('\n')
		complete_lines = process_sentences(remove_junk(line_list))
		complete_lines = [line.strip() for line in complete_lines]
		for line in complete_lines:
			parts = line.split(',')
			if len(parts) > 1:
				name = parts[0]
				if len(parts) == 2:
					job = "None"
					address = parts[1]			
				elif len(parts) > 2:
					job = parts[1]
					address = parts[2:]
				person = make_person(name, job, address)
				person = remove_name_from_job(person)
				new_name, rest = find_name(person)
				person['name'] = new_name.strip()
				file.write(f'{person}\nrest: {rest}\n\n')
	
	file.close()

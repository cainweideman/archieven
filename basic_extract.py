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

year = "1900"
path_to_json = f"book_text/{year}.json"

data = load_json(path_to_json)
first_page, last_page = 7, 248

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
				print(person)
				person_list.append(person)
		print('\n')
	
	print(f'Amount of people extracted: {len(person_list)}')

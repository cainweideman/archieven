import json
import re


def open_json(path_to_json):
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
		print(f"Error opening or parsing JSON file: {e}")
		return None


def get_text(data, first_page, last_page):
	"""
	Extracts text content from specified pages in the JSON data.

	Args:
		data (dict): JSON data containing the content.
		first_page (int): Starting page number (inclusive).
		last_page (int): Ending page number (inclusive).

	Returns:
		str: Concatenated text from the specified pages.
    """
	first_page_index = first_page -1
	last_page_index = last_page
	text_list = []

	for page in data['content'][first_page_index:last_page_index]:
		text = page['text']
		text_list.append(text)

	return ''.join(text_list)


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


def only_letters(text):
	"""
	Removes all non-letter characters from the text.

	Args:
		text (str): The input text.

	Returns:
		str: Text containing only letters.
	"""
	regex = re.compile("[^a-zA-Z]")
	return regex.sub('', text)


def remove_prepositions(sentence):
	prepositions_list = ['van', 'de', 'der', 'den', 'ter', 'ten', 'vander', 'v.', 'd', 'v', 'd.']
	sentence = [part for part in sentence if part not in prepositions_list]
	return sentence


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


def add_initial_dots(sentence):
	sentence = [string + "." if len(string) == 1 else string for string in sentence]
	return sentence


def split_on_initials(sentence):
	sentence_list = sentence.split()
	parts = sentence.split()[:4]

	initials_pattern = re.compile(r'^[A-Z](?:[.,])$')

	initials = []

	# Loop through the parts and find all initials
	for part in parts:
		part = part.strip()
		# Check if the part matches the initials pattern
		if initials_pattern.match(part):
			initials.append(part)

	num_initials = len(initials)
		
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
	address = parts[final_initial_position + 1:]
	rest = [i for i in sentence_list if i not in name]


	return name, rest


def split_job_and_street(sentence):
	sentence_list = sentence.split(',')
	if len(sentence_list) > 2:
		job = [sentence_list[0]]
		address = [i for i in sentence_list if i not in job]
	else:
		job = ''
		address = sentence_list
	
	return job, address

def extract_prepositions(sentence):
	sentence_list = sentence.split()
	prepositions_list = ['van', 'de', 'der', 'den', 'ter', 'ten', 'vander', 'v.', 'd', 'v', 'd.']
	prepositions = [part for part in sentence_list if part in prepositions_list]
	return prepositions


def format_name(name_list):
	prepositions_list = ['van', 'de', 'der', 'den', 'ter', 'ten', 'vander', 'v.', 'd', 'v', 'd.']

	initials = [part for part in name_list if re.match(r"^[A-Z]\.$", part)]
	prepositions = [part for part in name_list if part.lower() in prepositions_list]
	rest = [part for part in name_list if part not in initials and part not in prepositions]
	full_name_list = initials + prepositions + rest

	return ' '.join(full_name_list)


def make_json_object(name, job, address):
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


# Main execution
path_to_json = 'data/1880/text/1880.json'
data = open_json(path_to_json)
json_list = []

if data:
	text = get_text(data, first_page=34, last_page=151)
	text = strip_text(text)
	text = text.replace('\n\n', '\n')
	text_list = text.split('\n')

	for line in text_list:
		line_list = line.split(' ')
		line_list = remove_prepositions(line_list)
		sentence = " ".join(line_list)
		sentence = add_spaces(sentence)
		sentence = " ".join(add_initial_dots(sentence.split(' ')))
		name, rest = split_on_initials(sentence)
		prepositions = extract_prepositions(line)
		name = name + prepositions
		name = format_name(name)
		job, address = split_job_and_street(' '.join(rest))
		if len(name) >=1 and len(address) >= 1:
			person = make_json_object(name, ' '.join(job), ' '.join(address).strip().rstrip('.').strip())
			print(json.dumps(person, indent=2))
			json_list.append(person)

print(f'Amount of people extracted: {len(json_list)}')
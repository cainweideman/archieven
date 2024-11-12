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


def get_job_list(text_list):
    """
    Extracts potential job titles from a list of text lines based on specific criteria.

    A job title is considered valid if:
    - It starts with at least four uppercase characters.
    - It ends with at least three uppercase characters.
    - The line does not contain any digits.
    - The line length is greater than three characters (to filter out short words).

    Args:
        text_list (list): List of text lines.

    Returns:
        list: List of detected job titles that meet the criteria.
    """
    # Using list comprehension for more concise and efficient filtering
    job_list = [
        line for line in text_list
        if len(line) > 3  # Minimum length check
        and not any(chr.isdigit() for chr in line) # Ensures there are no digits
        and line.replace(' ', '')[:4].isupper()  # Checks if the first four characters are uppercase
        and line.replace(' ', '')[-3:].isupper()  # Checks if the last three characters are uppercase
    ]
    return job_list


def extract_lines(text):
    """
    Splits the text into sections based on job titles.

    Args:
        text (str): The input text.

    Returns:
        dict: A dictionary where the key is the job title and the value is the list of lines associated with it.
    """
    text_list = text.replace('\n\n', '\n').split('\n')
    job_list = get_job_list(text_list)
    index_list = [text_list.index(job) for job in job_list]
    job_dict = {}

    for i, first_index in enumerate(index_list):
        last_index = index_list[i + 1] if i < len(index_list) - 1 else len(text_list)
        job_dict[text_list[first_index]] = text_list[first_index + 1:last_index]

    return job_dict


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


def find_preposition(name_list, address_list):
    """
    Separates name prepositions (like 'van', 'de') from the address list.

    Args:
        name_list (list): List of name components.
        address_list (list): List of address components.

    Returns:
        tuple: Updated name list and address list.
    """
    prepositions_list = ['van', 'de', 'der', 'den', 'ter', 'ten', 'vander', 'v.', 'd', 'v', 'd.']
    address_list = [item.replace(',', '') for item in address_list]

    for prep in prepositions_list:
        if prep in address_list:
            name_list.append(prep)
            address_list.remove(prep)

    return name_list, address_list


def split_on_initials(sentence):
    """
    Splits a sentence into a name and an address based on initials.

    Args:
        sentence (str): The input sentence.

    Returns:
        tuple: List of name components and list of address components.
    """
    sentence = add_spaces(sentence)
    parts = sentence.split()
    initials_pattern = re.compile(r'^[A-Za-z](?:[.,])$')

    initials = [part for part in parts if initials_pattern.match(part)]
    final_initial_position = parts.index(initials[-1]) if initials else -1

    name = parts[:final_initial_position + 1]
    address = parts[final_initial_position + 1:]
    return find_preposition(name, address)


def format_name(name_list):
	"""
	Formats the name by combining initials, prepositions, and the rest of the name components.

	Args:
		name_list (list): List of name components.

	Returns:
		str: Formatted full name.
	"""
	prepositions_list = ['van', 'de', 'der', 'den', 'ter', 'ten', 'vander', 'v.', 'd', 'v', 'd.']
	initials = [part for part in name_list if re.match(r"^[A-Z]\.$", part)]
	prepositions = [part for part in name_list if part.lower() in prepositions_list]
	rest = [only_letters(part) for part in name_list if part not in initials and part not in prepositions]
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


def extract_people(job_dict):
    """
    Extracts people information from the job dictionary and prints a JSON object for each person.

    Args:
        job_dict (dict): Dictionary of job titles and associated lines of text.
    """
    for job, lines in job_dict.items():
        for line in lines:
            name, address = split_on_initials(line)
            if len(name) > 1 and address:
                if any(char.isdigit() for char in ' '.join(address)):
                    complete_name = format_name(name)
                    formatted_job = job[0].upper() + job[1:].lower().rstrip('.')
                    formatted_address = ' '.join(address).rstrip('.')
                    person = make_json_object(complete_name, formatted_job, formatted_address)
                    print(json.dumps(person, indent=2))
                    json_list.append(person)


# Main execution
path_to_json = 'data/1854/text/1854.json'
data = open_json(path_to_json)
json_list = []

if data:
	text = get_text(data, first_page=7, last_page=102)
	text = strip_text(text)
	job_dict = extract_lines(text)
	extract_people(job_dict)
	print(f'Amount of people extracted: {len(json_list)}')
	register = {
					'year': 1854,
					'register': json_list
				}
	json_object = json.dumps(register, indent=4)
	f = open('1854.json', 'w')
	f.write(json_object)
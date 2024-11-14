import json
import re


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


def check_for_person(input_string):
    if '(' in input_string or ')' in input_string:
        return True
    else:
        return False


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


def remove_unusable(line_list):
	new_line_list = []
	for line in line_list:
		if check_for_person(line) or any(char.isdigit() for char in line):
			new_line_list.append(line)
	
	return new_line_list


def complete_lines(sentences):
	result = []
	i = 0
	while i < len(sentences):
		# Check if the current sentence contains a person identifier
		if '(' in sentences[i] or ')' in sentences[i]:
			# If it's the last sentence, just add it to the result
			if i == len(sentences) - 1:
				result.append(sentences[i])
			else:
				# Check if the next sentence looks like a continuation
				if not ('(' in sentences[i + 1] or ')' in sentences[i + 1]):
					# Append the next line to the current one
					sentences[i] += " " + sentences[i + 1]
					# Skip the next line since it's been appended
					i += 1
				result.append(sentences[i].replace('\n', ''))
		else:
			# Add the line without changes if no person is detected
			result.append(sentences[i])
		i += 1
	return result


path_to_json = "book_text/1927.json"

data = load_json(path_to_json)

if data:
	last_line = ""
	text_list = get_text(data, 125, 610)
	for page in text_list:
		text = page.replace('\n\n', '\n')
		line_list = text.split('\n')
		new_line_list = remove_unusable(line_list)
		for line in complete_lines(new_line_list):
			print(repr(line))
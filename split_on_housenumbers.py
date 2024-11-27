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
		text = page['text'].replace('\n\n', '\n')
		text = text.replace('-\n', '')
		text = text.replace('\n', '')
		text_list.append(text)
		#text = text.replace('{', '(')
		#text = text.replace('}', ')')
		#text = text.replace('Mej.', '')
		#text = text.replace('Wed.', '')
		#text_list.append(text)

	return text_list


def split_by_housenumbers(text):
	"""
	Splits the input string based on housenumbers. A housenumber consists of 1-3 digits,
	optionally followed by a single letter, and ending with a punctuation mark.

	Args:
		text (str): The input string to split.

	Returns:
		list: A list of strings split by the housenumbers.
	"""
	#pattern = r'(\d{1,3}[A-Za-z]?[.,;!?\n])'
	pattern = r'(?<!\d)(\d{1,3}[A-Za-z]?[.,;!?\n])'
	return re.split(pattern, text)
	#return re.findall(pattern, text)


def split_text_with_housenumbers_included(text):
	"""
	Splits the input string based on housenumbers. Each housenumber is included 
	in the line preceding it in the resulting list.

	A housenumber consists of 1-3 digits, optionally followed by a single letter, 
	and ending with a punctuation mark or newline. It cannot be preceded by other digits.

	Args:
		text (str): The input string to split.

	Returns:
		list: A list of strings where each housenumber is part of the preceding segment.
	"""
    #pattern = r'(?<!\d)(\d{1,3}[A-Za-z]?[.,;!?\n])'
	pattern = r'(?<!\d)(\d{1,3}(?:[.,]\d{1,3})?[A-Za-z]?[.,;!?\n])'
	matches = re.finditer(pattern, text)

	# Keep track of the splits
	result = []
	last_end = 0

	for match in matches:
		start, end = match.span()
		# Include the current segment along with the housenumber
		result.append(text[last_end:end])
		last_end = end  # Update the position for the next split

	# Add the remaining text after the last match
	if last_end < len(text):
		result.append(text[last_end:])

	return result


def remove_phone_numbers(text):
    """
    Removes phone numbers from the string. Phone numbers are formatted like 
    'tel. 31033' (e.g., 'tel. ' followed by a number).

    Args:
        text (str): The input string from which to remove phone numbers.

    Returns:
        str: The text with phone numbers removed.
    """
    # Regex pattern to match phone numbers like 'tel. 31033'
    pattern = r'tel[.,]\s*\d{4,}'
    
    # Remove all occurrences of the pattern
    return re.sub(pattern, '', text)


year = "1958"
path_to_json = f"book_text/{year}.json"

# Load the JSON data from the specified path
data = load_json(path_to_json)
first_page, last_page = 84, 84

# Proceed if data is loaded successfully
if data:
	# Get text from specified pages
	text_list = get_text(data, first_page, last_page)

	# Process each page
	for index, page in enumerate(text_list):
		page_lines = []
		print(f'Page: {index + first_page}')
        
        # Split the page into lines and filter out unwanted lines
        #line_list = page.replace('\n\n', '\n').split('\n')
		#print(page)
		page_list = split_text_with_housenumbers_included(page)
		for i in page_list:
			line = remove_phone_numbers(i)
			print(repr(line))
		print('\n')
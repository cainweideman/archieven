from llama_index.core import PromptTemplate
import os
import pandas as pd
from tqdm import tqdm
from openai import Client,OpenAI
import json
import re


def System_Message(jsonschema):
    system_template = """
    You are an archive expert and your task is to extract required information from the OCR'ed text. Note that OCR'ed text might contain some errors.
	The text follows a fixed format:

    Name:
        The surname comes first, followed by initials (e.g., 'Jansen (A.B.)').
        Example: 'De Vries (J.)', 'Van Dijk (A.B.)'.

    Job Title (if available):
        Appears after the name, often separated by a comma.
        May be written in full or abbreviated (e.g., 'Dokter', 'Dr.', 'Ingenieur', 'Ir.', 'Werkman', 'Boekbindkn.', 'Metselaar', 'Agent').

    Address:
        Appears at the end of the sentence.
        Includes a street name and, if available, a house number (e.g., 'Hoofdstraat 12', 'Bakkerstraat').
		May be written in full or abbreviated (e.g., 'Verl. Hereweg', 'O. Ebbingestr.', 'Zuiderdiep', 'Gebr. Bakkerstraat').


    Output Format:{jsonschema}


	Extraction Requirements:

    Parse and extract the three fields: Name, Job Title, and Address.
    Handle minor OCR inconsistencies, such as extra spaces or missing punctuation.
    Ensure correct parsing even if the house number is missing in the address.
	If more persons can be found in the sentence, fill the JSON schema for all of them.

	Additional Considerations:
	- Use separators like commas, line breaks, and key phrases to distinguish elements.
    - Extract as much valid data as possible, even if the input text is incomplete or ambiguous.
	- Correct common OCR mistakes.
    """
    
    system_prompt = PromptTemplate(system_template)

    evaluated_system_prompt = system_prompt.format(jsonschema=jsonschema)

    return evaluated_system_prompt


def Human_Message(record):

    template = """jsonschema,
    Record: {record}

    Please extract the relavent information from the given record.
    """
    prompt = PromptTemplate(template)
    
    evaluated_human_prompt = prompt.format(
                        record = record
    )

    return evaluated_human_prompt


def ask_llama(system, user):
	messages = [{"role": "system", "content": system},
				{"role":"user","content":user}]


	completion = client.chat.completions.create(
		model=MODEL, 
		messages=messages
	)

	return completion.choices[0].message.content
    

schema = """
    Respond **ONLY** in valid JSON format, according to the following JSON schema:
    {
		"name": "",
		"jobTitle": "",
		"address": ""
	},
        "required": ["name", "jobTitle", "address"],
        "additionalProperties": false
    }

    
    Do NOT include the schema in your reply. Do NOT include any additional text outside of the JSON object.
    """


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
		text = text.replace('{', '(')
		#text = text.replace('}', ')')
		#text = text.replace('Mej.', '')
		#text = text.replace('Wed.', '')
		#text_list.append(text)

	return text_list


def strip_text(text):
	"""
	Removes special characters, keeping only alphanumeric characters, spaces, commas, periods, and newlines.

	Args:
		text (str): The input text.

	Returns:
		str: Cleaned text.
	"""
	regex = re.compile(r"[^a-zA-Z0-9\s,.\n'\-\(\)\{\}]")
	return regex.sub('', text)


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
    #pattern = r'tel[.,]\s*\d{4,}'
	#pattern = r'[Tt]el[.,]\s*\d{2,}'
	#pattern = r'[Tt]el(?:ef)?[.,]\s*\d+(\.\d+)*'
	#pattern = r'\b(?:[Tt]el|[Tt]elef)\.\s*\d+\b'
	pattern = r'\b(?:[Tt]el|[Tt]elef|[Tt]elefoon)\.\s*\d+\b'
    
    # Remove all occurrences of the pattern
	return re.sub(pattern, '', text)


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


def dot_initials(string):
	return re.sub(r'(?<=[A-Z])(?!\.)\b', '.', add_spaces(string))


def fix_initials_dot(line):
	"""
    Fixes initials by adding a period after the first capital letter.

    This function searches for pairs of an uppercase letter followed by a lowercase letter 
    (e.g., "A" followed by "b") in a string and adds a period after the uppercase letter, 
    effectively converting them into initials (e.g., "A." for "Ab").

    Args:
        line (str): The input string, which may contain initials or names.

    Returns:
        str: The string with corrected initials, where a period is added after the first capital letter.
    """
	pattern = r'\b([A-Z])([a-z])\b'
	return re.sub(pattern, r'\1.', line)


def fix_ocr_mistakes(text):
	"""
	Fixes OCR mistakes where the letter 'J' is mistaken for ')' or '}'.
	The function assumes the mistakes are in between '()' parentheses.
	"""
    #return re.sub(r'\(([^)]*)\)', lambda x: f'({x.group(1).replace(")", "J").replace("}", "J")})', text)
	#return re.sub(r'\([\s]*([^)]*)\)', lambda x: f'([\s]*{x.group(1).replace(")", "J").replace("}", "J")}[\s]*)', text)
	return re.sub(r'\(([^)]*)\)', lambda x: f'({x.group(1).replace(")", "J.").replace("}", "J.")})', text)


def replace_digits_parentheses(text):
    # Replace (1) with J, handling cases like (H. 1)
   # return re.sub(r'\(.*\s1\)', lambda match: match.group(0).replace('1', 'J'), text)
	updated_text = re.sub(r'\(.*[134].*\)', lambda match: match.group(0).replace('1', 'J.').replace('3', 'J').replace('4', 'J'), text)
	return updated_text


def make_page_json(page_number, person_list):
	page_object = {
			"page": page_number,
			"register": person_list
	}
	return json.dumps(page_object, indent=4)
	#return page_object


BASEURL = 'http://localhost:8000/v1/'
APIKEY = 'EMPTY'
MODEL = "meta-llama/Llama-3.1-8B-Instruct"

client = OpenAI(base_url=BASEURL,api_key=APIKEY)

year = "1926"
path_to_json = f"book_text/{year}.json"

# Load the JSON data from the specified path
data = load_json(path_to_json)
first_page, last_page = 121, 131

# Proceed if data is loaded successfully
if data:
	# Get text from specified pages
	text_list = get_text(data, first_page, last_page)

	# Process each page
	for index, page in enumerate(text_list):
		person_list = []
		page_number = index + first_page
		#print(f'Page: {index + first_page}')
        
        # Split the page into lines and filter out unwanted lines
        #line_list = page.replace('\n\n', '\n').split('\n')
		#print(page)
		page = strip_text(page)
		page_list = split_text_with_housenumbers_included(page)
		with_parentheses = [line for line in page_list if '(' in line or ')' in line]
		#print(with_parentheses)
		for i in with_parentheses:
			i = i.strip()
			line = remove_phone_numbers(i)
			if len(line) > 15 and len(line) < 150:
				line = dot_initials(line)
				line = re.sub(r'^[^a-zA-Z]+', '', line)
				line = replace_digits_parentheses(line)
				#print(repr(line))
				user = Human_Message(line)
				system = System_Message(jsonschema=schema)
				output = ask_llama(system, user)
				person_list.append(output)
				#print(output)
				#print(repr(line))
		page_object = make_page_json(page_number, person_list)
		print(page_object)
		print('\n')
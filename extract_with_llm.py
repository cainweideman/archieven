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
		May be written in full or abbreviated (e.g., 'Verl. Hereweg', 'O. Ebbingestr.', 'Zuiderdiep').


    Output Format:{jsonschema}


	Extraction Requirements:

    Parse and extract the three fields: Name, Job Title, and Address.
    Handle minor OCR inconsistencies, such as extra spaces or missing punctuation.
    Ensure correct parsing even if the house number is missing in the address.
	If multiple persons can be found in the sentence, extract all of them.

	Additional Considerations:
	- Use separators like commas, line breaks, and key phrases to distinguish elements.
    - Extract as much valid data as possible, even if the input text is incomplete or ambiguous.
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
		"name": {
			"type": "string",
			"description": "The name of the person or the company in the registry."
		},
		"address": {
			"type": "string",
			"description": "The address of the person or the company in the registry."
			},
		"jobTitle": {
			"type": "string",
			"description": "The occupation of the person in the registry."
			}
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
		text = page['text'].replace('-\n', '')
		text = text.replace('{', '(')
		text = text.replace('}', ')')
		text = text.replace('Mej.', '')
		text = text.replace('Wed.', '')
		text_list.append(text)

	return text_list


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


def find_initials(name):
	"""
    Finds initials in a given string and returns their positions.

    This function searches for single uppercase letters followed by a period (e.g., "A.") 
    within a string. It returns a list of matches where initials are found, including 
    the positions (start and end) of each match.

    Args:
        name (str): The name string to process, which may contain initials (e.g., "A.").

    Returns:
        list: A list of match objects found by the regex pattern. Each match represents 
              an initial (a single uppercase letter followed by a period) in the input string.
    """
	matches = list(re.finditer(r'\b[A-Z]\.', name))
	return matches


def combine_strings_with_initial(strings):
	"""
    Combines strings with initials and parentheses into a coherent format.

    This function processes a list of strings, looking for those that contain initials 
    and parentheses. It combines strings that are part of the same name or entry, 
    ensuring that initials and parentheses are correctly formatted and combined into 
    a single coherent string. The result is a list of combined strings, each representing 
    a properly formatted entry.

    Args:
        strings (list): A list of strings, each potentially containing initials and 
                        parentheses, which may need to be combined.

    Returns:
        list: A list of strings, where each string is a combined, properly formatted 
              version of the initial-separated entries from the input list.
    """
	combined = []
	current_combination = None
	found_valid_parenthesis = False

	for s in strings:
		# Check if the string contains '(' or ')' and an initial (e.g., "A.")
		has_parenthesis = '(' in s or ')' in s
		has_initial = find_initials(s)

		if not found_valid_parenthesis and not has_parenthesis:
			# Skip items until we find one with '(' or ')'
			continue

		if has_parenthesis and has_initial:
			if current_combination:  # Save the ongoing combination if any
				combined.append(current_combination)
			current_combination = s  # Start a new combination
			found_valid_parenthesis = True
		elif has_parenthesis and not has_initial:
			if found_valid_parenthesis:  # Append to the current combination if valid one exists
				current_combination += " " + s
			else:  # If no valid combination exists, treat it as standalone
				combined.append(s)
		elif found_valid_parenthesis:  # Attach to the current combination
			current_combination += " " + s

	# Append the last combination if there's any
	if current_combination:
		combined.append(current_combination)

	return combined


def find_prefixes(name):
	"""
    Finds prefixes such as 'v.', 'dt.', etc., in a name and returns the relevant section.

    This function searches for common prefixes (e.g., 'v.', 'dt.') in a given name. 
    It identifies these prefixes by using regular expressions and returns the 
    matched prefix along with the portion of the name that contains it. If no 
    prefix is found, the function returns an empty result.

    Args:
        name (str): The name string to process, potentially containing prefixes.

    Returns:
        str: The prefix found in the name, or an empty string if no prefix is found.
    """
	matches = list(re.finditer(r'(?:(?<=\s)|(?<=^)|(?<=\.))[vdt]\.?[a-z]{0,2}', name))
	if matches:
		last_match = matches[-1]  # Get the last match
		start_index = last_match.start() -1  # Start index of the last match
		end_index = last_match.end()  # End index of the last match (inclusive)
		return name[start_index:end_index]
	else:
		return matches  # No match found


def add_parenthesis_to_last_initial(text):
	"""
    Adds a closing parenthesis after the last initial in a string if it's missing.

    This function ensures that the last initial in a sequence of initials is properly formatted by adding a closing parenthesis 
    if it is not already present. It specifically targets initials that are followed by a space and ensures that the last initial 
    in the string is correctly enclosed in parentheses.

    Args:
        text (str): The input text containing initials that may be missing a closing parenthesis.

    Returns:
        str: The modified string with a closing parenthesis added after the last initial if needed.
    """
	# Regex pattern to find the last initial, remove the space after it, and add a closing parenthesis if not already present
	pattern = r'([A-Z])\.(?=\s)(?!\))'
	# Replace the last initial followed by space with the initial followed by a closing parenthesis
	text = re.sub(pattern, r'\1.)', text)

	# If there's no closing parenthesis already after the last initial, add it
	pattern_with_no_paren = r'([A-Z])\.(?=\s|$)(?!\))'
	return re.sub(pattern_with_no_paren, r'\1.)', text)


def clean_initials_in_parentheses(text):
	"""
    Cleans up initials inside parentheses by removing extra spaces and fixing formatting issues.

    This function addresses several common formatting problems with initials inside parentheses:
    - It removes any spaces before a closing parenthesis that appears after initials.
    - It ensures there is no space between a period and a closing parenthesis in initials.
    - It properly formats initials inside parentheses by removing unnecessary spaces and adding the closing parenthesis where needed.
    - It corrects instances where parentheses around initials are poorly formatted.

    Args:
        text (str): The input text containing initials inside parentheses.

    Returns:
        str: The cleaned-up text with properly formatted initials inside parentheses.
    """
	# Remove spaces before closing parenthesis after initials
	text = re.sub(r'\s*\)\s*', ')', text)

	# Remove space between period and closing parenthesis in initials
	text = re.sub(r'(\.\s*)(?=\))', '.', text)

	# Add closing parenthesis only after initials or sequence of initials preceded by '('
	text = re.sub(r'\(\s*([A-Z])\.(?=\s)(?!\))', r'(\1.)', text)  # For single initials
	text = re.sub(r'\(\s*([A-Z]\.\s*)+[A-Z]\.(?=\s|$)(?!\))', r'(\g<0>)', text)  # For multiple initials

	# Remove whitespace before an initial if preceded by '('
	text = re.sub(r'\(\s+([A-Z])\.', r'(\1.', text)

	return text

def remove_false_parenthesis(text):
	"""
    Removes false or misplaced parentheses from the input text.

    This function addresses specific cases where parentheses are incorrectly placed:
    - It removes empty parentheses `()` that are used incorrectly, replacing them with just a single opening parenthesis `(`.
    - It removes closing parentheses `)` that appear immediately after initials without proper context.

    Args:
        text (str): The input text containing misplaced or false parentheses.

    Returns:
        str: The cleaned text with false parentheses removed or corrected.
    """
	text = re.sub(r'\(\s*\)', '(', text)  # Remove `)` if only preceded by a `(`
	text = re.sub(r'([A-Z])\.\s*\)(?=\s+[A-Z])', r'\1.', text)  # Remove `)` between initials

	return text


def split_by_initials(text):
	"""
	Splits the input text into segments based on surnames and initials within parentheses.

	This function uses a regular expression to detect and separate surnames followed by initials enclosed 
	in parentheses, and the remaining text following those names and initials. The result is a list where 
	each entry consists of a surname with initials and any text that follows it.

	Args:
		text (str): The input text containing names with initials and additional content.

	Returns:
		list: A list of strings, where each string is a segment consisting of a surname with initials 
				(e.g., "Doe (J. D.)") followed by the remaining text (e.g., "address details").
	"""
    # Regex pattern to match surnames followed by initials
	pattern = r'([A-Z][a-zÀ-ÿ]*(?:\s[A-Z][a-zÀ-ÿ]*)*)\s\(([A-Z]\.\s?)+\)'

	# Use re.split to split the sentence based on matches
	segments = re.split(pattern, text)

	# Combine the surname and initials back into each matched segment, and filter out empty strings
	results = []
	for i in range(1, len(segments), 3):  # Iterate over matched parts
		surname_initial = segments[i] + " (" + segments[i+1] + ")"
		remaining_text = segments[i+2].strip()
		results.append(surname_initial + remaining_text)

	return results


def split_by_name(text):
	"""
    Splits the text by name and the remainder after the name.

    Args:
        text (str): The input text.

    Returns:
        tuple: A tuple with two lists: one for names and one for the rest of the text.
    """
	pattern = r'([A-Za-zÀ-ÿ]+(?:\s?\([^\)]*\)))\s*(.*?)(?=[A-Za-zÀ-ÿ]+\s?\([^\)]*\)|$)'

    # Find all matches (each match will be a tuple: (name, remainder))
	matches = re.findall(pattern, text)

	name = [match[0].strip() for match in matches]
	# Return a list of the remainders without the names
	remainders = [match[1].strip() for match in matches]

	return name, remainders


def split_by_initials_with_context(text):
	"""
    Splits the text by surname and initials, while preserving context.

    Args:
        text (str): The input text.

    Returns:
        list: List of segments split by surname-initial pairs.
    """
    # Define a regex pattern to capture surname-initial pairs
	pattern = r'([A-Za-zÀ-ÿ]+(?:\s?\([^\)]*\)))[^A-Za-zÀ-ÿ]*'
    
    # Find all matches for names (surnames followed by initials)
	matches = re.finditer(pattern, text)
    
    # Store the start and end positions of each match
	spans = [(match.start(), match.end()) for match in matches]

	# Extract corresponding sentences for each match
	segments = []
	for i, (start, end) in enumerate(spans):
		# Start of current match
		name = text[start:end]
		# End at the start of the next match or the end of the text
		next_start = spans[i + 1][0] if i + 1 < len(spans) else len(text)
		# Append the text from the current match to the next match
		segments.append(text[start:next_start].strip())

	return segments


def find_prefixes(text):
	"""
    Finds prefixes such as 'v.', 'dt.', etc., in a name and returns the relevant section.

    This function searches for common prefixes (e.g., "v.", "dt.") within a string. It looks for patterns
    where the prefix is followed by lowercase letters and may optionally end with a period. The function 
    returns the prefix if it is found, along with the remainder of the text after the prefix.

    Args:
        text (str): The text string to search for prefixes.

    Returns:
        tuple: A tuple containing the prefix (str) and the remaining text (str). If no prefix is found, 
               an empty list and an empty string are returned.
    """
	matches = list(re.finditer(r'\b[vdt][\w.]{0,2}\)', text))
	if matches:
		last_match = matches[-1]  # Get the last match
		start_index = last_match.start() -1  # Start index of the last match
		end_index = last_match.end()  # End index of the last match (inclusive)
		prefix = text[:end_index]
		rest = text[end_index:]
		return prefix, rest
	else:
		return matches, ''  # No match found
	


BASEURL = 'http://localhost:8000/v1/'
APIKEY = 'EMPTY'
MODEL = "meta-llama/Llama-3.1-8B-Instruct"

client = OpenAI(base_url=BASEURL,api_key=APIKEY)

if __name__ == "__main__":
	year = "1927"
	path_to_json = f"book_text/{year}.json"

	# Load the JSON data from the specified path
	data = load_json(path_to_json)
	first_page, last_page = 125, 610

	# Proceed if data is loaded successfully
	if data:
		# Get text from specified pages
		text_list = get_text(data, first_page, last_page)

		# Process each page
		for index, page in enumerate(text_list):
			page_lines = []
			print(f'Page: {index + first_page}')
			
			# Split the page into lines and filter out unwanted lines
			line_list = page.replace('\n\n', '\n').split('\n')
			line_list = [
				line for line in line_list 
				if len(''.join(char for char in line if char.isalpha())) > 3 and 
				('(' in line or ')' in line or any(char.isdigit() for char in line))
			]
			
			# Combine strings with initials and process them
			complete_lines = combine_strings_with_initial(line_list)

			# Further processing: fixing initials and handling lines with digits
			complete_lines_with_digits = [
				dot_initials(fix_initials_dot(line)) for line in complete_lines if any(char.isdigit() for char in line)
			]

			# Clean up initials and handle false parentheses
			new_lines = [
				clean_initials_in_parentheses(line) for line in complete_lines_with_digits
			]
			new_lines = [
				remove_false_parenthesis(line) for line in new_lines
			]

			# Split the lines based on initials with context
			split_lines = [split_by_initials_with_context(line) for line in new_lines]

			# Add processed lines to page_lines
			for i, line in enumerate(split_lines):
				if line:
					page_lines.extend(line)  # Add each part of the split line
				else:
					page_lines.append(new_lines[i])  # If no split, keep the original line

			# Process each line to extract names and the corresponding rest of the text
			for i in page_lines:
				if len(i) < 1000:
					print(i)
					user = Human_Message(i)
					system = System_Message(jsonschema=schema)
					output = ask_llama(system, user)
					print(output)
					print('\n')
				
			print('\n')  # Print a newline after each page


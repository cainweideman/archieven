from fuzzywuzzy import process
import json


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


def get_persons(data):
	"""
	Extracts text content from specified pages in the JSON data.

	Args:
		data (dict): JSON data containing the content.
		first_page (int): Starting page number (inclusive).
		last_page (int): Ending page number (inclusive).

	Returns:
		str: Concatenated text from the specified pages.
    """
	person_list = [person for person in data['register']]
	return person_list


def get_street_list(path_to_streets='streets.txt'):
	f = open('streets.txt', 'r')
	street_list = f.read().splitlines()
	f.close()

	return street_list


def correct_street_name(person, street_list, threshold=80):
	address = person['address'].replace('0.', 'O.')
	address_list = address.split()
	address_list = [part for part in address_list if not any(char.isdigit() for char in part)]
	print(address)
	streetname = ''.join(address_list)
	match, score = process.extractOne(streetname, street_list)
	if score > threshold:
		print(f'Corrected: {match}')
		#return match
	else:
		print(f'Not Corrected: {" ".join(address_list)}')
		#return address


#text = "Achterweg 7. 4974"
#print(correct_street_name(text.split()[0], street_list, threshold=50))
data = open_json("1854.json")
person_list = get_persons(data)
for person in person_list:
	correct_street_name(person, get_street_list(), threshold=70)
	print('\n')


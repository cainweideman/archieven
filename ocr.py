import pytesseract
from PIL import Image
import os
import json

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

directory = 'cleaned/1968'
filenames = os.listdir(directory)

data = {
	"year": 1968,
	"content": []
}

content = []

for index, filename in enumerate(filenames): # Go through files
	f = os.path.join(directory, filename) # Get path to file
	print(f) # Print File name
	image = Image.open(f) # Open the image
	text = pytesseract.image_to_string(image, lang='nld') # Perform OCR and save text
	page = {
		"page": index + 1,
		"text": text
	}
	content.append(page)

data["content"] = content
json_string = json.dumps(data, indent=4)
outfile = open('text/1968.json', 'a+')
outfile.write(json_string + '\n')
outfile.close()
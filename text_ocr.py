import pytesseract
from PIL import Image
import os
import json

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

directory = 'data/1854/images_improved'
filenames = os.listdir(directory)


for index, filename in enumerate(filenames): # Go through files
	f = os.path.join(directory, filename) # Get path to file
	print(f) # Print File name
	image = Image.open(f) # Open the image
	text = pytesseract.image_to_string(image, lang='nld') # Perform OCR and save text
	print(text)
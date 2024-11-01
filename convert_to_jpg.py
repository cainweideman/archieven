import fitz
import os

root_directory = 'data'
directories = os.listdir(root_directory)

for directory in directories:
	path = os.path.join(root_directory, directory)
	filenames = os.listdir(path)
	file_path = os.path.join(path, filenames[0])

	output_directory = os.path.join(path, 'images')
	if not os.path.exists(output_directory):
		os.makedirs(output_directory)

	doc = fitz.open(file_path)

	for i in range(len(doc)):
		page = doc.load_page(i)
		zoom = 2
		mat = fitz.Matrix(zoom, zoom)
		image = page.get_pixmap(matrix = mat, dpi = 200)
		page_number = f"{i:04}"
		output_filename = str(directory) + '_page_' + page_number + '.jpg'
		output_path = os.path.join(output_directory, output_filename)
		image.save(output_path)

	doc.close()
	print(directory)
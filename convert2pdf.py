import os
import img2pdf


output_folder = 'cleaned/1968'
image_files = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]

with open('1964.pdf', 'wb') as f:
	f.write(img2pdf.convert(image_files))
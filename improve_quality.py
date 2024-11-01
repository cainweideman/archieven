import cv2
from matplotlib import pyplot as plt
import os


def display(im_path):
    dpi = 80
    im_data = plt.imread(im_path)

    height, width  = im_data.shape[:2]
    
    # What size does the figure need to be in inches to fit the image?
    figsize = width / float(dpi), height / float(dpi)

    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    # Hide spines, ticks, etc.
    ax.axis('off')

    # Display the image.
    ax.imshow(im_data, cmap='gray')

    plt.show()


def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


#image_file = 'cleaned/1968/1968_page_0008.jpg'
#img = cv2.imread(image_file)

#display(image_file)

#gray_image = grayscale(img)
#cv2.imwrite("temp/gray.jpg", gray_image)


#thresh, im_bw = cv2.threshold(gray_image, 200, 230, cv2.THRESH_BINARY)
#cv2.imwrite("temp/bw_image.jpg", im_bw)


#cropped = img[50:1880, 50:1200]
#cv2.imwrite("temp/cropped.jpg", cropped)
#display("temp/cropped.jpg")

root_directory = 'data'
directories = os.listdir(root_directory)

for directory in directories:
	path = os.path.join(root_directory, directory)
	filenames = os.listdir(path)
	file_path = os.path.join(path, filenames[-2])
	
	output_directory = os.path.join(path, 'images_improved')
	if not os.path.exists(output_directory):
		os.makedirs(output_directory)

	for image in os.listdir(file_path):
		output_file = "improved_" + image
		image_path = os.path.join(file_path, image)
		img = cv2.imread(image_path)
		gray_image = grayscale(img)
		thresh, im_bw = cv2.threshold(gray_image, 160, 230, cv2.THRESH_BINARY)
		height, width = img.shape[:2]
		top = int(height * 0.05)
		bottom = int(height * (1 - 0.05))
		left = int(width * 0.05)
		right = int(width * (1 - 0.05))
		cropped_img = im_bw[top:bottom, left:right]
		cv2.imwrite(os.path.join(output_directory, output_file), cropped_img)
### Installing Anaconda on Windows

Here’s a comprehensive guide to installing Anaconda on Windows, creating and managing environments, and installing packages with Conda.

---

#### Step 1: Download and Install Anaconda

1. **Download Anaconda**:
   - Go to the [Anaconda download page](https://www.anaconda.com/products/distribution).
   - Select the Windows installer and download the version compatible with your system (usually 64-bit).

2. **Run the Installer**:
   - Open the downloaded `.exe` file to start the installation.
   - Follow the prompts and choose the recommended settings. This typically includes adding Anaconda to your PATH, which simplifies using Anaconda from the command line.
   - Complete the installation.

3. **Verify Installation**:
   - Open the **Anaconda Prompt** (search for it in the Start menu).
   - Run the command:
     ```bash
     conda --version
     ```
   - If installed correctly, you should see the version number displayed.

---

#### Step 2: Create an Anaconda Environment

1. **Open Anaconda Prompt**:
   - Open the **Anaconda Prompt** from your Start menu.

2. **Create a New Environment**:
   - To create a new environment with a specific Python version, use:
     ```bash
     conda create -n myenv python=3.11
     ```
     Replace `myenv` with the name you want for your environment, and `3.11` with your desired Python version.

3. **Confirm Environment Creation**:
   - You may be prompted to confirm package downloads. Type `y` and press Enter to proceed.

---

#### Step 3: Activate and Deactivate an Environment

1. **Activate the Environment**:
   - In Anaconda Prompt, activate your environment with:
     ```bash
     conda activate myenv
     ```
     Replace `myenv` with the name of your environment.

2. **Deactivate the Environment**:
   - To return to the base environment, simply type:
     ```bash
     conda deactivate
     ```

---

#### Step 4: Install Packages in an Environment

1. **Installing Packages with Conda**:
   - Once in your desired environment, you can install packages with Conda. For example:
     ```bash
     conda install numpy
     ```
   - You can also specify the channel (like `conda-forge`) for specific packages if needed:
     ```bash
     conda install -c conda-forge pandas
     ```

2. **Verifying Installed Packages**:
   - To see a list of installed packages in your environment, use:
     ```bash
     conda list
     ```

---

Your Anaconda installation and environment setup are now complete! You can now install additional packages and manage multiple environments for different projects.

### Guide: Selecting a New Conda Environment in Spyder or Visual Studio Code

Once you’ve created a new Conda environment, you can configure Spyder or Visual Studio Code to use it. Here’s how to select your new environment in both editors.

---

#### 1. Selecting a Conda Environment in Spyder

1. **Launch Spyder**:
   - If you haven't installed Spyder in your environment yet, you can do so by activating your environment in the Anaconda Prompt and running:
     ```bash
     conda install spyder
     ```
   - After installation, launch Spyder from this environment using:
     ```bash
     spyder
     ```

2. **Set the Python Interpreter**:
   - In Spyder, go to **Tools > Preferences**.
   - Select **Python Interpreter** from the sidebar.
   - Choose **Use the following Python interpreter** and click **Browse**.
   - Navigate to your environment’s `python.exe` file:
     - Typically located at: `C:\Users\YourUsername\anaconda3\envs\your_env_name\python.exe`
   - Click **Apply** and **OK**.

3. **Restart Spyder**:
   - Restart Spyder for the changes to take effect. It will now use the selected environment.

---

#### 2. Selecting a Conda Environment in Visual Studio Code

1. **Open Visual Studio Code**.

2. **Install the Python Extension**:
   - If you haven’t installed it already, go to the **Extensions** sidebar and search for **Python** by Microsoft.
   - Click **Install**.

3. **Select the Interpreter**:
   - Press **Ctrl + Shift + P** (or **Cmd + Shift + P** on macOS) to open the command palette.
   - Type **Python: Select Interpreter** and select it.
   - VS Code will show a list of available Python interpreters, including Conda environments.
   - Choose the interpreter associated with your environment, which should look something like this:
     ```plaintext
     (your_env_name) C:\Users\YourUsername\anaconda3\envs\your_env_name\python.exe
     ```

4. **Verify Environment**:
   - Open a terminal within VS Code (**View > Terminal**) to ensure that the selected environment is active.
   - You can confirm by running:
     ```bash
     python --version
     ```
   - It should show the Python version specific to your selected environment.

5. **Install Packages**:
   - If you need to install any packages within this environment, you can activate the terminal with the selected environment and use Conda or pip to install as needed.

---

Now, you can seamlessly use your Conda environment in Spyder or VS Code!
 
 <br />
 <br />
 <br />

### Installing Pytesseract with Tesseract OCR on Windows

Here’s a step-by-step guide to install Pytesseract and set up Tesseract OCR with additional language support for Dutch (Flemish).

---

#### Step 1: Install Pytesseract in Conda Environment

1. Open your terminal or Anaconda Prompt.
2. Run the following command to install `pytesseract` from the `conda-forge` channel:
   ```bash
   conda install -c conda-forge pytesseract
   ```

---

#### Step 2: Install Tesseract OCR on Your PC

1. **Download Tesseract**:
   - Go to the [Tesseract OCR Installation page](https://github.com/UB-Mannheim/tesseract/wiki).
   - Download the 64-bit Windows installer: `tesseract-ocr-w64-setup-5.4.0.20240606.exe`.
   
2. **Run the Installer**:
   - Launch the downloaded `.exe` file to start installation.
   - During installation, select **Dutch (Flemish)** under additional language options if you need OCR for that language.

---

#### Step 3: Add Tesseract OCR to Your PATH

1. Open **Edit System Environment Variables**.
2. Click on **Environment Variables**.
3. Under **User Variables**, select **Path** and click **Edit**.
4. Click **New** and add the following path:
   ```
   C:\Program Files\Tesseract-OCR
   ```

---

#### Step 4: Configure Tesseract Path in Python Script

To make sure Python can find Tesseract OCR, add this line to your Python script:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
```

---

Your Pytesseract setup is now complete! You’re ready to use Tesseract OCR in Python for text extraction from images, with support for Dutch and Flemish if you selected it during installation.

 <br />
 <br />
 <br />

### Guide: Using the Image Processing Script

This guide explains how to use the image processing script provided. This script processes images within a specified directory structure by converting them to grayscale, binarizing (black and white), cropping them, and saving the processed images to a designated subfolder.

---

#### 1. Prerequisites

Make sure you have installed the required packages:
- **OpenCV (cv2)**: Install with:
  ```bash
  conda install opencv
  ```

#### 2. Directory Structure Setup

Before running the script, set up your directory structure as shown below:
```plaintext
root_directory/
    ├── subdirectory1/
    │   ├── images/
    │   │   └── image1.jpg
    │   └── images_improved/   # This will be created automatically for processed images
    ├── subdirectory2/
    │   ├── images/
    │   │   └── image2.jpg
    │   └── images_improved/
```

- `root_directory`: The main folder containing subdirectories for image processing.
- `images`: Each subdirectory should contain an `images` folder with the images you want to process.
- `images_improved`: The script will create this folder in each subdirectory to store the processed images.

---

#### 3. Script Functions Overview

1. **`grayscale`**: Converts an image to grayscale.
2. **`binarize_image`**: Converts the grayscale image to black and white.
3. **`crop_image`**: Crops a margin from each edge of the image.
4. **`process_images_in_directory`**: Processes images in all directories under `root_directory`.
5. **`process_image`**: Processes a single image.
6. **`process_directory`**: Processes all images within a single directory.

---

#### 4. Running the Script

You can use the functions in three ways:

1. **Process a Single Image**:
   - To process just one image, specify its path and use `process_image`. 
   - Example:
     ```python
     path_to_image = "data/1854/images/1854_page_0006.jpg"
     process_image(path_to_image, threshold=170, crop_fraction=0.05)
     ```
   - This will display the processed image in a pop-up window.

2. **Process All Images in One Directory**:
   - To process all images in a specific directory, use `process_directory`.
   - Set `path_to_directory` to the desired directory and call:
     ```python
     path_to_directory = "data/1854"
     process_directory(path_to_directory, threshold=170, crop_fraction=0.05)
     ```
   - Processed images will be saved to `images_improved` in this directory.

3. **Process Images in All Subdirectories**:
   - To process all images in multiple subdirectories, use `process_images_in_directory`.
   - Set `root_directory` to the main directory and call:
     ```python
     root_directory = "data"
     process_images_in_directory(root_directory, threshold=170, crop_fraction=0.05)
     ```
   - The script will iterate through each subdirectory and save processed images in `images_improved`.

---

#### 5. Adjusting Parameters

- **Threshold**: The `threshold` parameter (default `160`) controls the binarization. Lower values make the image darker.
- **Crop Fraction**: The `crop_fraction` (default `0.05`) defines how much of each edge to crop. A value of `0.05` removes 5% of the image from each side.

---

#### Example Usage

Here's how to adjust and use the parameters for your processing needs:

```python
# Parameters
threshold = 170  # Adjust for binarization intensity
crop_fraction = 0.05  # Adjust to change the margin cropped from each edge

# Run for a single image
path_to_image = "data/1854/images/1854_page_0006.jpg"
process_image(path_to_image, threshold, crop_fraction)

# Run for one directory
path_to_directory = "data/1854"
process_directory(path_to_directory, threshold, crop_fraction)

# Run for all directories
root_directory = "data"
process_images_in_directory(root_directory, threshold, crop_fraction)
```

---

By following these steps, you can effectively use the script to process your images for grayscale conversion, binarization, cropping, and saving in a well-organized folder structure.

<br />
<br />
<br />

### Guide: Using the OCR Processing Script

This guide walks you through setting up and using the OCR Processing Script to perform OCR on images in a specified directory. The script extracts text from images and saves the results in a structured JSON file.

---

#### Prerequisites
- **Tesseract OCR**: Download and install Tesseract OCR.
    - Windows users: You can get the installer from [this link](https://github.com/UB-Mannheim/tesseract/wiki).
    - Add Tesseract to your PATH:
      - **Open** `Edit System Environment Variables` > **Environment Variables**.
      - In **User Variables**, find `Path`, click **Edit** > **New**, and add:
        ```
        C:\Program Files\Tesseract-OCR
        ```
- **Python Packages**: Install required packages (`pytesseract`, `Pillow`, `os`, and `json`).

To install packages:
```bash
conda install -c conda-forge pytesseract
```

```bash
conda install pillow
```

---

### Using the Script

The script contains two main functions:

#### 1. **Perform OCR on a Single Image**: `ocr_page`

This function reads a single image, performs OCR, and returns the text as a string.

**Example Usage**:
   ```python
   path_to_image = "data/1854/images_improved/improved_1854_page_0012.jpg"
   print(ocr_page(path_to_image, config="4"))
   ```

- **Parameters**:
  - `path_to_image`: File path of the image to be processed.
  - `language`: Language code (default: `"nld"` for Dutch).
  - `config`: Page segmentation mode (default: `"3"`; see segmentation mode options in the script).

#### 2. **Perform OCR on All Images in a Directory**: `ocr_directory`

This function processes all images in a specified directory, extracting text and saving it in a JSON file.

**Example Usage**:
   ```python
   path_to_images_directory = "data/1854/images_improved"
   output_directory = "data/1854"
   ocr_directory(path_to_images_directory, output_directory, config="4")
   ```

- **Parameters**:
  - `path_to_images_directory`: Path to the folder containing the images.
  - `output_directory`: Path to the folder where the JSON output will be saved.
  - `language`: Language code for OCR (default: `"nld"`).
  - `config`: Page segmentation mode.

**Output Format**:
The output JSON file is structured as follows:
```json
{
    "year": "1854",
    "content": [
        {"page": 1, "text": "Extracted text for page 1..."},
        {"page": 2, "text": "Extracted text for page 2..."},
        ...
    ]
}
```
- The JSON file is saved in an `output_directory/text` subfolder, with the filename set to the year extracted from `path_to_images_directory` (e.g., `1854.json`).

---

### Configuration Options

**Page Segmentation Modes**:
- The default mode (`config="3"`) is suitable for full-page text recognition.
- For single columns, text blocks, or custom needs, adjust the `config` parameter according to the list in the script (e.g., `"4"` for single-column text).

---

### Running the Script

1. **OCR a Specific Image**:
   Uncomment and customize the following code in the script:
   ```python
   path_to_image = "data/1854/images_improved/improved_1854_page_0012.jpg"
   print(ocr_page(path_to_image, config="4"))
   ```

2. **OCR All Images in a Directory**:
   Uncomment and set up:
   ```python
   path_to_images_directory = "data/1854/images_improved"
   output_directory = "data/1854"
   ocr_directory(path_to_images_directory, output_directory, config="4")
   ```

3. **Run the Script**: Execute the script from the terminal:
   ```bash
   python ocr_script.py
   ```

This will process the specified images, applying OCR, and saving the results in structured JSON format for easy retrieval and analysis.

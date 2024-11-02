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

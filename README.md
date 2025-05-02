# Document Scanner text Recognition and Translation with Python
A Python-based application for scanning documents from images, recognizing text using OCR, translating it into another language, and overlaying the translated text back onto the document. It uses OpenCV for image processing, Tesseract for optical character recognition (OCR), and Deep Translator for translation.

---

## Features

- Upload or select an image (camera, phone, or file).
- Automatic or manual document cropping.
- Image preprocessing (grayscale and thresholding) for enhanced OCR accuracy.
- Optical Character Recognition (Tesseract).
- Text translation using Google Translate (via Deep Translator).
- Translated text is placed directly onto the original document image.
- Saves original and translated text as `.txt` files.
- Saves final translated image.

---

## Installation

Install Tesseract OCR:

On Windows, download and install it, then set the path in the script:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

## Requirements
Python 3.7+
OpenCV
pytesseract
deep-translator
tkinter (usually included with Python)
NumPy

You can install them with:
pip install opencv-python pytesseract deep-translator numpy

## How It Works
~Image Input
The user selects an image file using a dialog box.

~Preprocessing
The image is converted to grayscale and thresholded to enhance OCR performance.

~Cropping
The document is automatically cropped using contour detection. If unsuccessful or unsatisfactory, manual cropping is available via mouse clicks.

~OCR (Text Recognition)
Text is extracted using Tesseract OCR.

~Translation
Extracted text is translated using the Deep Translator (Google Translate API).

~Overlay Translated Text
The translated text is drawn onto the original document image.

~Output
The program saves the final image, original text, and translated text.

Screenshots
![image](https://github.com/user-attachments/assets/f4fd338d-244b-4438-bb81-ee902d1d7091)
![image](https://github.com/user-attachments/assets/c3396e1d-be2b-4626-acaa-97700b0c0120)

Made by Robotic srudents, Merzhan, Anuar and Tanirbergen. Feel free to contribute or fork the project!

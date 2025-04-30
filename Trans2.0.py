import cv2
import pytesseract
import numpy as np
from deep_translator import GoogleTranslator
import tkinter as tk
from tkinter import filedialog

# Path to Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to select an image file via dialog box
def select_image():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    return file_path

# Load the image
image_path = select_image()
if not image_path:
    print("No image selected.")
    exit()

# Load the image with support for paths containing non-ASCII characters
image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)

if image is None:
    print(" Failed to load the image.")
    exit()

# Function to select a region of interest (ROI) in the image
def select_roi(image):
    print("Click and drag to select the area to translate.")
    roi = cv2.selectROI("Select Area", image, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    return roi

# Select the region
roi = select_roi(image)
if roi == (0, 0, 0, 0):
    print("No area selected.")
    exit()

# Crop the selected region from the image
x, y, w, h = roi
selected_area = image[y:y+h, x:x+w]

# Recognize text and word coordinates in the selected area
ocr_data = pytesseract.image_to_data(selected_area, lang='rus', output_type=pytesseract.Output.DICT)

# Process each detected word
for i in range(len(ocr_data['text'])):
    word = ocr_data['text'][i].strip()
    if word == '':
        continue

    x_text, y_text = ocr_data['left'][i], ocr_data['top'][i]
    w_text, h_text = ocr_data['width'][i], ocr_data['height'][i]

    # Translate the word
    try:
        translated_word = GoogleTranslator(source='ru', target='en').translate(word)
    except Exception as e:
        print(f" Translation error for '{word}': {e}")
        translated_word = word

    # Cover the original word with a white rectangle
    cv2.rectangle(selected_area, (x_text, y_text), (x_text + w_text, y_text + h_text), (255, 255, 255), -1)

    # Write the translated word in place of the original
    cv2.putText(selected_area, translated_word, (x_text, y_text + h_text - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

# Insert the translated region back into the original image
image[y:y+h, x:x+w] = selected_area

# Save the final image
output_path = image_path.rsplit('.', 1)[0] + "_translated.jpg"
cv2.imwrite(output_path, image)

print(f"\n Translated image saved as: {output_path}")
cv2.imshow("Translated Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

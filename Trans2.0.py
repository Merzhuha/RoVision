import cv2
import pytesseract
import numpy as np
from deep_translator import GoogleTranslator
import tkinter as tk
from tkinter import filedialog

# Path to Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to select an image file via dialog box
def select_image():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    return file_path

# Load the image
path = select_image()
if not path:
    print("❌ Image not selected.")
    exit()

# Load image with Cyrillic characters in path
img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

if img is None:
    print("❌ Failed to load the image.")
    exit()

# Function to select a region (ROI) in the image
def select_roi(image):
    print("Click and drag to select the translation area.")
    roi = cv2.selectROI("Select Area", image, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    return roi

# Select the region
roi = select_roi(img)
if roi == (0, 0, 0, 0):
    print("❌ No area selected.")
    exit()

# Extract the selected region from the image
x, y, w, h = roi
selected_region = img[y:y+h, x:x+w]

# Recognize text and coordinates in the selected area
data = pytesseract.image_to_data(selected_region, lang='rus', output_type=pytesseract.Output.DICT)

for i in range(len(data['text'])):
    word = data['text'][i].strip()
    if word == '':
        continue

    x_text, y_text, w_text, h_text = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

    # Translate
    try:
        translated = GoogleTranslator(source='ru', target='en').translate(word)
    except Exception as e:
        print(f"⚠️ Translation error for '{word}': {e}")
        translated = word

    # Cover the original text
    cv2.rectangle(selected_region, (x_text, y_text), (x_text + w_text, y_text + h_text), (255, 255, 255), -1)

    # Apply the translated text
    cv2.putText(selected_region, translated, (x_text, y_text + h_text - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

# Insert the translated region back into the image
img[y:y+h, x:x+w] = selected_region

# Save the result
output_path = path.rsplit('.', 1)[0] + "_translated.jpg"
cv2.imwrite(output_path, img)

print(f"\n✅ Translated image saved as: {output_path}")
cv2.imshow("Translated Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()  
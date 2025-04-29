import cv2
import numpy as np
import pytesseract
from deep_translator import GoogleTranslator
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os

# Укажи путь к Tesseract, если нужно
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Хранилище для точек
points = []

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def click_event(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            cv2.circle(param, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(param, f"{len(points)}", (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            cv2.imshow("Выделите документ (4 точки)", param)

def preprocess_for_ocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)         # серое изображение
    blur = cv2.GaussianBlur(gray, (5, 5), 0)               # сглаживаем шум
    thresh = cv2.adaptiveThreshold(blur, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY,
                                   11, 2)                  # адаптивный порог
    return thresh

def manual_crop(image_path):
    global points
    points = []
    
    # Чтение изображения через np.fromfile + imdecode (чтобы работало с кириллицей в пути)
    try:
        image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"❌ Ошибка при чтении изображения: {e}")
        return None, None

    if image is None:
        print("❌ Не удалось загрузить изображение.")
        return None, None

    clone = image.copy()
    cv2.imshow("Выделите документ (4 точки)", clone)
    cv2.setMouseCallback("Выделите документ (4 точки)", click_event, clone)
    print("🖱 Кликните 4 угла документа слева направо по часовой (или против часовой)")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or len(points) == 4:
            break

    cv2.destroyAllWindows()

    if len(points) != 4:
        print("❌ Выбрано недостаточно точек.")
        return None, None

    pts = np.array(points, dtype="float32")
    cropped = four_point_transform(image, pts)
    output_path = image_path.rsplit('.', 1)[0] + "_manual_crop.jpg"
    
    # Сохраняем тоже через imencode + fromfile (если путь с кириллицей)
    try:
        ext = output_path.split('.')[-1]
        success, buffer = cv2.imencode(f'.{ext}', cropped)
        if success:
            with open(output_path, 'wb') as f:
                f.write(buffer)
    except Exception as e:
        print(f"⚠️ Ошибка при сохранении: {e}")

    return output_path, cropped

def recognize_and_translate(image, output_base_path):
    preprocessed = preprocess_for_ocr(image)
    text = pytesseract.image_to_string(preprocessed, lang='eng')
    original = text.strip()
    print("\n📜 Распознанный текст:\n", original)

    # Пути для сохранения
    original_txt = output_base_path + "_original_text.txt"
    translated_txt = output_base_path + "_translated_text.txt"

    if original:
        try:
            translated = GoogleTranslator(source='auto', target='ru').translate(original)
            print("\n📘 Перевод:\n", translated.strip())

            # Сохраняем оба текста
            with open(original_txt, "w", encoding="utf-8") as f:
                f.write(original)

            with open(translated_txt, "w", encoding="utf-8") as f:
                f.write(translated.strip())

            print(f"\n💾 Сохранено:")
            print(f" - Оригинал: {original_txt}")
            print(f" - Перевод: {translated_txt}")

        except Exception as e:
            print(f"\n⚠️ Ошибка перевода: {e}")
    else:
        print("⚠️ Текст не распознан.")

def main():
    # Открываем диалог выбора файла
    Tk().withdraw()  # Скрыть главное окно Tkinter
    image_path = askopenfilename(
        title="Выберите изображение документа",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
    )

    if not image_path:
        print("❌ Файл не выбран.")
        return

    print(f"📂 Выбран файл: {image_path}")
    cropped_path, cropped_img = manual_crop(image_path)

    if cropped_img is not None:
        recognize_and_translate(cropped_img, cropped_path.rsplit('.', 1)[0])
        print(f"\n✅ Документ сохранён: {cropped_path}")
    else:
        print("❌ Операция отменена.")

if __name__ == "__main__":
    main()

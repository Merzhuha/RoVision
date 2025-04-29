
import cv2
import numpy as np
import pytesseract
from deep_translator import GoogleTranslator
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os

# Укажи путь к Tesseract, если нужно
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
    width = image.shape[1]
    height = image.shape[0]
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (width, height))
    return warped

def click_event(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            cv2.circle(param, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(param, f"{len(points)}", (x+5, y-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            cv2.imshow("Выделите документ (4 точки)", param)

def preprocess_for_ocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY,
                                   11, 2)
    return thresh

def manual_crop(image_path, original_image):
    global points
    points = []

    clone = original_image.copy()
    cv2.imshow("Выделите документ (4 точки)", clone)
    cv2.setMouseCallback("Выделите документ (4 точки)", click_event, clone)
    print("🖱 Кликните 4 угла документа")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or len(points) == 4:
            break

    cv2.destroyAllWindows()

    if len(points) != 4:
        print("❌ Выбрано недостаточно точек.")
        return None, None

    pts = np.array(points, dtype="float32")
    cropped = four_point_transform(original_image, pts)
    output_path = image_path.rsplit('.', 1)[0] + "_manual_crop.jpg"
    ext = output_path.split('.')[-1]
    success, buffer = cv2.imencode(f'.{ext}', cropped)
    if success:
        with open(output_path, 'wb') as f:
            f.write(buffer)
    return output_path, cropped

def recognize_and_translate(image, output_base_path):
    preprocessed = preprocess_for_ocr(image)
    text = pytesseract.image_to_string(preprocessed, lang='eng')
    original = text.strip()
    print("\n📜 Распознанный текст:\n", original)

    original_txt = output_base_path + "_original_text.txt"
    translated_txt = output_base_path + "_translated_text.txt"

    if original:
        try:
            translated = GoogleTranslator(source='auto', target='ru').translate(original)
            print("\n📘 Перевод:\n", translated.strip())

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
    Tk().withdraw()
    image_path = askopenfilename(
        title="Выберите изображение документа",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
    )
    if not image_path:
        print("❌ Файл не выбран.")
        return

    print(f"📂 Выбран файл: {image_path}")
    image = cv2.imdecode(
        np.fromfile(image_path, dtype=np.uint8),
cv2.IMREAD_COLOR
    )
    if image is None:
        print("❌ Не удалось загрузить изображение.")
        return

    # Попытка автообрезки
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 75, 200)
    contours, _ = cv2.findContours(
        edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    screenCnt = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            screenCnt = approx.reshape(4, 2)
            break

    if screenCnt is not None:
        auto_crop = four_point_transform(image, screenCnt)
        cv2.imshow("Автообрезка – Enter для продолжения, R – ручной режим", auto_crop)
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()

        if key == ord('r'):
            print("🔁 Переход в ручной режим...")
            cropped_path, cropped_img = manual_crop(image_path, image)
        else:
            cropped_img = auto_crop
            cropped_path = image_path.rsplit('.', 1)[0] + "_auto_crop.jpg"
            ext = cropped_path.split('.')[-1]
            success, buffer = cv2.imencode(f'.{ext}', cropped_img)
            if success:
                with open(cropped_path, 'wb') as f:
                    f.write(buffer)
    else:
        print("⚠️ Автообрезка не удалась. Ручной режим...")
        cropped_path, cropped_img = manual_crop(image_path, image)

    if cropped_img is not None:
        recognize_and_translate(cropped_img, cropped_path.rsplit('.', 1)[0])
        cv2.imshow("📄 Конечный результат", cropped_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print(f"\n✅ Документ сохранён: {cropped_path}")
    else:
        print("❌ Операция отменена.")

# Здесь исправленное условие точки входа:
if __name__== "__main__":
    main()

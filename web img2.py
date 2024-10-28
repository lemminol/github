import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO
import pytesseract
from googletrans import Translator

def download_image(url):
    response = requests.get(url)
    img_data = BytesIO(response.content)
    return Image.open(img_data)

def translate_text(text, dest_language='ko'):
    translator = Translator()
    translated = translator.translate(text, dest=dest_language)
    return translated.text

def overlay_text_on_image(image, text):
    img = image.copy()
    draw = ImageDraw.Draw(img) # type: ignore
    draw.text((10, 10), text, fill="white")
    return img

def download_and_translate():
    url = url_entry.get()
    original_image = download_image(url)
    extracted_text = pytesseract.image_to_string(original_image)
    translated_text = translate_text(extracted_text)
    result_image = overlay_text_on_image(original_image, translated_text)

    result_image.show()

app = tk.Tk()
app.title("Image Translator")

url_label = tk.Label(app, text="Image URL:")
url_label.pack()

url_entry = tk.Entry(app, width=50)
url_entry.pack()

translate_button = tk.Button(app, text="Download and Translate", command=download_and_translate)
translate_button.pack()

app.mainloop()

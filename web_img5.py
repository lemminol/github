import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import cv2
from google.cloud import vision
from google.cloud import translate_v2 as translate
import io
from PyQt5 import QtWidgets
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PIL import Image, ImageQt, ImageFilter
from io import BytesIO
import requests
from google.cloud import vision
from google.cloud import translate_v2 as translate
import os

# Google Cloud Vision API Key 설정 (사전에 설정해야 합니다)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'Google Cloud Vision API Key 경로.json'  # Google Cloud Vision API Key 경로로 변경

# Google Cloud Translate API Key 설정 (사전에 설정해야 합니다)
translate_client = translate.Client()   # Google Cloud Translate API Client 생성

# Google Cloud Vision API Client 생성
vision_client = vision.ImageAnnotatorClient()

# Tesseract OCR Engine 경로 설정 (Windows, MacOS, Linux)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Tesseract OCR Engine 경로로 변경

class ImageTranslator(QWidget):
    def __init__(self):
        super().__init__()
        # UI 구성
        self.layout = QVBoxLayout() 
        self.setLayout(self.layout) 
        self.url_label = QLabel('URL 입력:')    
        self.url_edit = QLineEdit()
        self.translate_button = QPushButton('번역') 
        self.image_label = QLabel()
        self.result_label = QLabel()
        self.layout.addWidget(self.url_label)
        self.layout.addWidget(self.url_edit)
        self.layout.addWidget(self.translate_button)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.result_label)
        self.translate_button.clicked.connect(self.translate_image)
        
    def translate_image(self):
        url = self.url_edit.text()
        image_bytes = self.download_image(url)
        if image_bytes is None:
            self.result_label.setText('이미지 다운로드 실패')
            return
        text = self.extract_text(image_bytes)
        if text is None:
            self.result_label.setText('텍스트 추출 실패')
            return
        translated_text = self.translate_text(text)
        self.result_label.setText(translated_text)
        self.display_image(image_bytes)

    def download_image(self, url):
        # requests 라이브러리를 사용하여 이미지 다운로드
        try:
            response = requests.get(url)
            response.raise_for_status() # 오류 상태 코드에 대해 예외 발생
            return io.BytesIO(response.content)
        except requests.RequestException as e:
            print(f"이미지 다운로드 실패: {str(e)}")
            return None
        
    def extract_text(self, image_bytes):
        try:
            img = Image.open(image_bytes)
            img = img.convert('L')  # 그레이스케일로 변환
            img = img.filter(ImageFilter.MedianFilter())  # 노이즈 제거
            img.verify()  # 파일이 손상되었는지 확인
            text = pytesseract.image_to_string(img, lang='jpn+jpn+vert', config='--psm 6')  # 다중 언어, 페이지 세분화 설정
            return text.strip()  # 추출된 텍스트의 앞뒤 공백 제거
        except Exception as e:
            print(f"텍스트 추출 실패: {str(e)}")
            return None
        
    def translate_text(self, text, target_language='ko'):  # 기본 대상 언어를 영어로 설정
        try:
            translated = translate_client.translate(text, target_language=target_language)
            return translated['translatedText']
        except Exception as e:
            print(f"번역 실패: {str(e)}")
            return None
    
    def save_image_with_text(image_bytes, translated_text):
        try:
            img = Image.open(image_bytes)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 20)  # 폰트 설정
            draw.text((10, 10), translated_text, font=font, fill=(255, 0, 0))  # 번역된 텍스트를 이미지에 추가
            img.save("translated_image.jpg")  # 이미지 저장
            print("번역된 이미지가 저장되었습니다.")
        except Exception as e:
            print(f"이미지 저장 실패: {str(e)}")
            return None
    
    def display_image_with_text(self, image_bytes, translated_text):
        try:
            img = Image.open(image_bytes)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 20)  # 폰트 설정
            draw.text((10, 10), translated_text, font=font, fill=(255, 0, 0))  # 번역된 텍스트를 이미지에 추가
            qt_img = ImageQt.ImageQt(img)
            pixmap = QtGui.QPixmap.fromImage(qt_img)
            self.image_label.setPixmap(pixmap)
            self.image_label.setAlignment(QtCore.Qt.AlignCenter)
            self.image_label.show()
            self.result_label.setText(translated_text)
            # 번역된 텍스트를 결과 레이블에 표시
            return True
        except Exception as e:
            print(f"이미지 표시 실패: {str(e)}")
            return None
            return False

    
    def display_image(self, image_bytes):
        try:
            img = Image.open(image_bytes)
            qt_img = ImageQt.ImageQt(img)
            pixmap = QtGui.QPixmap.fromImage(qt_img)
            self.image_label.setPixmap(pixmap)
            self.image_label.setAlignment(QtCore.Qt.AlignCenter)
            self.image_label.show()
        except Exception as e:
            print(f"이미지 표시 실패: {str(e)}")
            return None

# PyQt5 애플리케이션 실행
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageTranslator() 
    window.setWindowTitle('Image Translator')
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())

# 이 코드는 PyQt5를 사용하여 이미지 URL을 입력받고, 해당 이미지에서 텍스트를 추출한 후 번역하는 간단한 애플리케이션입니다. 이미지 다운로드, 텍스트 추출, 번역, 이미지 표시 등의 기능을 수행합니다. 코드를 실행하기 전에 필요한 라이브러리를 설치하고, Google Cloud Vision API Key와 Google Cloud Translate API Key를 설정해야 합니다. 또한 Tesseract OCR Engine의 경로를 설정해야 합니다.

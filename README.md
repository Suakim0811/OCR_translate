# OCR_translater
## 1. 개요
11주차 과제로 제출하였던 기획안을 바탕으로 제작하였음.  
구글의 Circle To Search에서 착안한 화면 캡쳐 번역기를 구현하는 것이 본 프로젝트의 목적임  

<br>

**주요 기능**
-   화면 영역 선택 및 캡쳐
-	이미지에서 텍스트 추출 (OCR)
-	추출된 텍스트 자동 번역
-   클립보드에 번역 결과 복사   
<br>
  
## 2. 기초 설명
### 시스템 환경
- **하드웨어 요구사항**
    -	운영체제: Windows 10/11  

- **소프트웨어 요구사항**
    -	Python 3.8 이상 
    -	Tesseract OCR
    -	인터넷 연결 (번역 API 사용 위함)

### 제약 조건
-	인터넷 연결이 필요함 (Google 번역 API 사용)
-	Tesseract OCR 엔진이 사전 설치되어 있어야 함
-	OCR 정확도는 이미지 품질에 의존함

### 사용 라이브러리
|라이브러리|버전|용도|
|---|---|---|
|tkinter|기본(내장)|GUI 구현|
|requests|2.31|번역 사이트 접근|
|pyperclip|1.8+|클립보드 복사|
|Pytesseract|0.3.10+|이미지에서 텍스트 추출|
|Pillow(PIL)|10.0+|이미지 처리|
|ctypes|기본(내장)|해상도 문제 처리|
<br>

## 3. 코드 동작 흐름

### 1. 프로그램 실행 
```
if __name__ == "__main__":
    app = TranslatorApp()
    app.run()
```
```
class TranslatorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Translator")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
        self.setup_ui()
...
```
1. `TranslatorApp()` 객체 생성  
2. `__init__()` 실행  
3. `setup_ui()` 메인 GUI 구성  
4. `root.mainloop()` 이벤트 대기  
<br>

### 2. 메인 GUI 생성 (TranslatorApp 클래스)
```
self.root = tk.Tk()
self.root.title("Translator")
self.root.geometry("800x600")
```
메인 창 구성  




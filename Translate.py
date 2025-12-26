import requests
import tkinter as tk
from tkinter import scrolledtext
# ▲ 기존 사용한 라이브러리 ▲
import pyperclip
from PIL import ImageGrab, Image
import pytesseract
import ctypes
# ▲ NEW ▲


# 해상도 문제(캡쳐시 화면 1/4가 확대되어 전체를 메움) 해결, AI의 도움...
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor DPI Aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

# 테서렉트 설치 경로 설정(이 작업 없이는 테서렉트가 작동을 안 함), AI의 도움...
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 기존 코드 그대로
def translate(text, target='ko'):
    url = "https://translate.google.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": target,
        "dt": "t",
        "q": text
    }
    result = requests.get(url, params=params).json()
    return result[0][0][0]

def extract_text_from_image(image):
    """이미지에서 영어 추출(OCR)"""
    text = pytesseract.image_to_string(image, lang='eng')
    return text.strip()

class ScreenCaptureOverlay:
    """캡쳐 && 영역 선택"""
    def __init__(self, callback):
        self.callback = callback # 캡쳐 후 실행될 함수
        self.start_x = None
        self.start_y = None # 마우스 클릭 좌표
        self.rect = None # 선택 영역
        
        self.screenshot = ImageGrab.grab() #이미지 캡쳐
        
        self.overlay = tk.Toplevel() # 메인과는 다른 Gui
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-topmost', True)
        self.overlay.configure(cursor="cross")
        

        """
	    pillow와 tkinter가 쓰는 이미지가 다르기 때문에 형식을 바꿔줘야 함. 
        pillow 이미지가 공장에서 제조되는 커피 원액이라면 tkinter 이미지는 캔에 담긴 커피. 
        캔커피 판매원에게 통 없이 원액만 가져다주면 많이 당혹스러울 것
        """
        self.tk_image = tk.PhotoImage(data=self._image_to_data(self.screenshot)) 


        self.canvas = tk.Canvas(self.overlay, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        
        self.canvas.create_rectangle(0, 0, self.screenshot.width, self.screenshot.height, 
                                     fill='black', stipple='gray50', tags='overlay')
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.overlay.bind("<Escape>", self.on_cancel)
        
    def _image_to_data(self, image):
        """필로우 이미지를 tkinter가 읽을 수 있게 변환"""
        import io
        buffer = io.BytesIO()
        image.save(buffer, format='PNG') # 이미지를 메모리에 png로 저장
        return buffer.getvalue()
    
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )
    
    def on_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
    
    def on_release(self, event):
        if self.start_x is None or self.start_y is None:
            return
            
        end_x, end_y = event.x, event.y
        
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        if x2 - x1 < 10 or y2 - y1 < 10:
            self.overlay.destroy()
            return
        
        cropped = self.screenshot.crop((x1, y1, x2, y2))
        
        self.overlay.destroy()
        self.callback(cropped)
    
    def on_cancel(self, event):
        self.overlay.destroy()

class TranslatorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Translator")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
        self.setup_ui()
        
    def setup_ui(self):
        # 캡쳐 버튼
        capture_btn = tk.Button(
            self.root, text="화면 캡쳐하기", 
            command=self.start_capture,
            bg="#4a7abc", fg="white", 
            font=("휴먼둥근헤드라인", 12, "bold"),
            activebackground="#5a8acc", activeforeground="white"
        )
        capture_btn.pack(pady=10)
        
        # 인식된 원문
        origin_label = tk.Label(
            self.root, text="인식된 원문 (영어):", 
            fg="white", bg="#1e1e1e", 
            font=("휴먼둥근헤드라인", 11)
        )
        origin_label.pack(anchor="w", padx=10, pady=5)
        
        self.origin_text = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, height=8, 
            bg="#2d2d2d", fg="white", 
            font=("휴먼둥근헤드라인", 10)
        )
        self.origin_text.pack(fill="both", padx=10, pady=5, expand=True)
        
        lang_label = tk.Label(
            self.root, text="대상 언어 코드 (예: ko, en, ja):", 
            fg="white", bg="#1e1e1e", 
            font=("휴먼둥근헤드라인", 11)
        )
        lang_label.pack(anchor="w", padx=10, pady=5)

        self.lang_entry = tk.Entry(
            self.root, bg="#2d2d2d", fg="white", 
            font=("휴먼둥근헤드라인", 10)
        )
        self.lang_entry.pack(fill="x", padx=10, pady=5)
        self.lang_entry.insert(0, "ko")
     
        result_label = tk.Label(
            self.root, text="번역 결과:", 
            fg="white", bg="#1e1e1e", 
            font=("휴먼둥근헤드라인", 11)
        )
        result_label.pack(anchor="w", padx=10, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, height=8, 
            bg="#2d2d2d", fg="white", 
            font=("휴먼둥근헤드라인", 10)
        )
        self.result_text.pack(fill="both", padx=10, pady=5, expand=True)
        self.result_text.config(state="disabled")
        
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(pady=10)
        
        translate_btn = tk.Button(
            btn_frame, text="번역하기", 
            command=self.do_translate,
            bg="#3a3a3a", fg="white", 
            font=("휴먼둥근헤드라인", 11, "bold"),
            activebackground="#505050", activeforeground="white"
        )
        translate_btn.pack(side="left", padx=5)
        
        copy_btn = tk.Button(
            btn_frame, text="클립보드에 저장", 
            command=self.copy_to_clipboard,
            bg="#3a3a3a", fg="white", 
            font=("휴먼둥근헤드라인", 10, "bold"),
            activebackground="#505050", activeforeground="white"
        )
        copy_btn.pack(side="left", padx=5)
    
    def start_capture(self):
        """화면 캡쳐 시작"""
        self.root.withdraw()  # 창 숨김
        self.root.after(200, self._do_capture) 
    
    def _do_capture(self):
        """캡쳐"""
        ScreenCaptureOverlay(self.on_capture_complete)
    
    def on_capture_complete(self, image):
        """캡쳐 완료 후 처리"""
        self.root.deiconify()  # 메인 창 다시 표시
        
        if image:
            try:
                extracted_text = extract_text_from_image(image)
                
                # 원문 텍스트 영역에 표시
                self.origin_text.delete("1.0", tk.END)
                self.origin_text.insert(tk.END, extracted_text)
                
                if extracted_text:
                    # 자동으로 번역
                    self.do_translate()
            except Exception as e:
                self.origin_text.delete("1.0", tk.END)
                self.origin_text.insert(tk.END, f"OCR 오류: {str(e)}\n\n테서렉트 인식 안 됨")
    
    def do_translate(self):
        """번역"""
        origin = self.origin_text.get("1.0", tk.END).strip()
        target = self.lang_entry.get().strip()
        
        if origin and target:
            try:
                translated = translate(origin, target)
                self.result_text.config(state="normal")
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END, translated)
                self.result_text.config(state="disabled")
            except Exception as e:
                self.result_text.config(state="normal")
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert(tk.END, f"번역 오류: {str(e)}")
                self.result_text.config(state="disabled")
    
    def copy_to_clipboard(self):
        self.result_text.config(state="normal")
        text = self.result_text.get("1.0", tk.END).strip()
        self.result_text.config(state="disabled")
        pyperclip.copy(text)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TranslatorApp()
    app.run()

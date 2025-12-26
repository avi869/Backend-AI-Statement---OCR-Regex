
import cv2
import pytesseract
import os

# Path to the actual uploaded image
# Note: I'll copy it to scratch to access it easily or read directly
image_path = r"C:\Users\ASUS\.gemini\antigravity\brain\b1acec18-d068-4883-b496-9abf3fcb2210\uploaded_image_1765651344122.png"
config = r'--oem 3 --psm 6'

def test_ocr(path):
    try:
        print(f"Testing OCR on: {path}", flush=True)
        if not os.path.exists(path):
            print("File not found!", flush=True)
            return

        img = cv2.imread(path)
        if img is None:
            print("Failed to load image!", flush=True)
            try:
                # Debugging: check file size
                print(f"File size: {os.path.getsize(path)} bytes", flush=True)
            except:
                pass
            return
        
        # Standard Approach
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Experiment 1: Simple Threshold
        _, thresh1 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        text1 = pytesseract.image_to_string(thresh1, config=config)
        
        # Experiment 2: OTSU Threshold (Current implementation)
        gray_blur = cv2.medianBlur(gray, 3)
        _, thresh2 = cv2.threshold(gray_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Resize like current implementation
        scale_percent = 150
        width = int(thresh2.shape[1] * scale_percent / 100)
        height = int(thresh2.shape[0] * scale_percent / 100)
        resized = cv2.resize(thresh2, (width, height), interpolation=cv2.INTER_LINEAR)
        
        text2 = pytesseract.image_to_string(resized, config=config)
        
        print("\n--- Exp 1 (Simple Thresh) ---", flush=True)
        print(text1[:500], flush=True) # Print first 500 chars
        
        print("\n--- Exp 2 (Current Logic: OTSU + Resize) ---", flush=True)
        print(text2[:500], flush=True)
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}", flush=True)


if __name__ == "__main__":
    test_ocr(image_path)

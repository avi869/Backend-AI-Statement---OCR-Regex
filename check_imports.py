
import sys

log = []

def check(name, lambda_import):
    try:
        lambda_import()
        log.append(f"{name}: OK")
    except Exception as e:
        log.append(f"{name}: FAILED - {e}")
    except SystemExit:
         log.append(f"{name}: FAILED - SystemExit")

check("numpy", lambda: __import__('numpy'))
# check("cv2", lambda: __import__('cv2')) # cv2 often crashes hard, let's do it individually if needed
# Check others
check("pytesseract", lambda: __import__('pytesseract'))
check("pdf2image", lambda: __import__('pdf2image'))
check("fastapi", lambda: __import__('fastapi'))

with open("diagnosis.txt", "w") as f:
    f.write("\n".join(log))

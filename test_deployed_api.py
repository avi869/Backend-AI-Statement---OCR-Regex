import requests
import os
import sys

# Write to log file
log_file = open("deployment_test_log.txt", "w", encoding="utf-8")
def log(msg):
    print(msg)
    log_file.write(str(msg) + "\n")
    log_file.flush()

url = "https://backend-ai-statement-ocr.onrender.com/extract-transactions"
file_path = r"c:\Users\ASUS\.gemini\antigravity\scratch\bank_ocr\uploads\9df389bb-49ee-43fa-868c-c504d591ee7c.pdf"

log(f"Testing API at {url}")
log(f"Uploading {file_path}")

try:
    if not os.path.exists(file_path):
        log(f"File not found: {file_path}")
        exit(1)

    with open(file_path, "rb") as f:
        files = {"file": ("test_statement.pdf", f, "application/pdf")}
        response = requests.post(url, files=files)

    log(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        log("Success!")
        data = response.json()
        log(f"Transaction Count: {data.get('transaction_count')}")
        log("Formatted Output Preview:")
        log(data.get("formatted_output", "")[:500])
    else:
        log("Failed!")
        log(response.text)

except Exception as e:
    log(f"Error: {e}")

log_file.close()


import requests
import os

url = "http://127.0.0.1:8000/extract-transactions"
file_path = r"C:/Users/ASUS/.gemini/antigravity/brain/d2e83e36-5c88-4907-8427-39e70904b9fa/uploaded_image_1765824147310.jpg"

print(f"Testing API at {url}")
print(f"Uploading {file_path}")

try:
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(response.json())
    
    # Save formatted output to a file for viewing
    if response.status_code == 200:
        data = response.json()
        with open("api_formatted_output.txt", "w", encoding="utf-8") as out:
            out.write(data.get("formatted_output", "No output field"))
        print("\nSaved formatted result to api_formatted_output.txt")

except Exception as e:
    print(f"Error: {e}")

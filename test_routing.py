import sys
import os

# Add the project directory to sys.path
sys.path.append(r'c:\Users\ASUS\.\gemini\antigravity\scratch\bank_ocr')

from main import detect_date_format

def test_detection():
    test_cases = [
        ("Transactions on 10/23/2025 were processed", "MM/DD/YYYY"),
        ("Date of payment: 23/10/2025", "DD/MM/YYYY"),
        ("Oct 23, 2025 Paid to RAKESH", "MM/DD/YYYY"),
        ("14 Dec Paid to Harendra", "DD/MM/YYYY"), # Falls back to DD/MM/YYYY
        ("No dates here", "DD/MM/YYYY"), # Default fallback
    ]
    
    with open("test_log.txt", "w", encoding="utf-8") as out:
        out.write("Testing Date Format Detection...\n")
        all_passed = True
        for text, expected in test_cases:
            result = detect_date_format(text)
            if result == expected:
                out.write(f"✅ PASSED: '{text[:30]}...' -> {result}\n")
            else:
                out.write(f"❌ FAILED: '{text[:30]}...' -> Got {result}, Expected {expected}\n")
                all_passed = False
                
        if all_passed:
            out.write("\n✨ All detection tests passed!\n")
        else:
            out.write("\n⚠️ Some detection tests failed.\n")

if __name__ == "__main__":
    test_detection()

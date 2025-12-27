import sys
import os

# Add the project directory to sys.path
sys.path.append(r'c:\Users\ASUS\.gemini\antigravity\scratch\bank_ocr')

from main import format_transactions_text

def test_format():
    transactions = [
        {"Date": "Oct 23, 2025", "Type": "DEBIT", "Amount": "40.00", "Category": "Personal", "Description": "Paid to RAKESH KUMAR"},
        {"Date": "Oct 21, 2025", "Type": "DEBIT", "Amount": "150.14", "Category": "Mobile", "Description": "Mobile recharged 8986721145"},
        {"Date": "Oct 18, 2025", "Type": "DEBIT", "Amount": "756.00", "Category": "Flipkart", "Description": "Paid to Flipkart"},
        {"Date": "Oct 01, 2025", "Type": "CREDIT", "Amount": "300.00", "Category": "Personal", "Description": "Received from ANAM ANSARI"},
        {"Date": "Sep 30, 2025", "Type": "CREDIT", "Amount": "10000.00", "Category": "Mr", "Description": "Received from Mr Abhishek Kumar Jha"},
    ]
    
    formatted = format_transactions_text(transactions)
    print("--- NEW FORMATTED OUTPUT ---")
    print(formatted)
    print("----------------------------")
    
    with open("format_test_output.txt", "w", encoding="utf-8") as f:
        f.write(formatted)

if __name__ == "__main__":
    test_format()

import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from bank_statement_ocr import parse_transactions
from main import format_transactions_text

# Mock OCR Output based on User Examples
mock_ocr_text = """
Oct 23, 2025
Paid to Rakesh Kumar DEBIT 40

Oct 18, 2025
Paid to Flipkart DEBIT 756

Oct 21, 2025
Mobile recharged DEBIT 150.14

Oct 01, 2025
Received from ANAM ANSARI CREDIT 7300

Sep 30, 2025
Received from Abhishek Kumar Jha CREDIT 10000

Oct 11, 2025
Paid to Flipkart Internet Pvt Ltd DEBIT 186

Oct 05, 2025
Mobile recharged DEBIT 304.33

Oct 10, 2025
Paid to Ahsan Ansari DEBIT 349

Oct 05, 2025
Paid to Rahul Momo DEBIT 80
"""

print("--- Running Parse ---")
transactions = parse_transactions(mock_ocr_text)

print(f"Parsed {len(transactions)} transactions.")
for t in transactions:
    print(f"[{t['Date']}] {t['Description']} -> {t['Category']} ({t['Type']} {t['Amount']})")

print("\n--- Running Format ---")
formatted_output = format_transactions_text(transactions)
print("\n--- Writing Format to 'verification_result.txt' ---")
with open('verification_result.txt', 'w', encoding='utf-8') as f:
    f.write(formatted_output)
print("Done.")

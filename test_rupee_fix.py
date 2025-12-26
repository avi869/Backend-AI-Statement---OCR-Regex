
import sys
import os

sys.path.append(os.getcwd())
from bank_statement_ocr import parse_transactions

# Mock OCR text with the artifacts user described
mock_text = """
Oct 23, 2025
Paid to Rakesh Kumar DEBIT 740

Oct 21, 2025
Mobile recharged DEBIT 2150.14
"""


print("--- Testing Rupee Artifact Fix ---", flush=True)
try:
    with open("rupee_final_result.txt", "w", encoding="utf-8") as f:
        transactions = parse_transactions(mock_text)
        for t in transactions:
            line = f"Original Description: {t['Description']}\nExtracted Amount: {t['Amount']} (Expected: 40 or 150.14)\n{'-'*20}\n"
            print(line)
            f.write(line)
    print("Test Complete. Wrote to rupee_final_result.txt", flush=True)
except Exception as e:
    print(f"CRITICAL ERROR: {e}", flush=True)


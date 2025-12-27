import sys
import os

# Add the project directory to sys.path
sys.path.append(r'c:\Users\ASUS\.gemini\antigravity\scratch\bank_ocr')

import bank_statement2_ocr

def test_refinement():
    test_text = """
14 Dec 10:20 PM Paytm Bus: Bhubaneswar-Sambalpur O Tag: Ae Axis Bank - Rs.690.64
Bank Ref No: 7657310568696735205910
Order ID: 26344266780

14 Dec 5:17 PM Paid to Harendra Saw Tag: BB Bank Of - Rs.20
UPI ID: q815477717@ybl on PhonePe
UPI Ref No: 695568090142

13 Dec 3:39 PM Paid to Deepak Kumar O Tag: B} Bank Of - Rs.68
UPI ID: q287781922@ybl on PhonePe
UPI Ref No: 695500954068

13 Dec 1:51 PM Money sent to Suraj Kumar © Tag: 3 Bank Of - Rs.170
UPI ID: 7277059375@ibl ON @ PhonePe
UPI Ref No: 393723042744

12 Dec 1:21 PM Paid to Mr Sanjay Malakar © Tag: B3 Bank Of - Rs.35
UPI ID: sanjay@ybl on PhonePe
"""

    transactions = bank_statement2_ocr.parse_transactions(test_text)
    
    print("--- REFINEMENT TEST RESULTS ---")
    all_passed = True
    
    # Expected results based on user request
    expected = [
        {"Desc": "Paytm Bus: Bhubaneswar-Sambalpur", "Cat": "Paytm", "Amt": "690.64"},
        {"Desc": "Paid to Harendra Saw", "Cat": "Harendra", "Amt": "20"},
        {"Desc": "Paid to Deepak Kumar", "Cat": "Deepak", "Amt": "68"},
        {"Desc": "Money sent to Suraj Kumar", "Cat": "Money", "Amt": "170"},
        {"Desc": "Paid to Mr Sanjay Malakar", "Cat": "Mr", "Amt": "35"},
    ]
    
    with open("refinement_results.txt", "w", encoding="utf-8") as out:
        for i, (t, exp) in enumerate(zip(transactions, expected)):
            desc_ok = t['Description'] == exp['Desc']
            cat_ok = t['Category'] == exp['Cat']
            amt_ok = t['Amount'] == exp['Amt']
            
            status = "✅" if desc_ok and cat_ok and amt_ok else "❌"
            msg = f"{status} Row {i+1}: Desc: '{t['Description']}' (Exp: '{exp['Desc']}'), Cat: '{t['Category']}' (Exp: '{exp['Cat']}'), Amt: '{t['Amount']}' (Exp: '{exp['Amt']}')\n"
            print(msg, end="")
            out.write(msg)
            
            if not desc_ok or not cat_ok:
                all_passed = False
                
        if all_passed:
            out.write("\n✨ All refinement tests passed!\n")
            print("\n✨ All refinement tests passed!")
        else:
            out.write("\n⚠️ Some refinement tests failed.\n")
            print("\n⚠️ Some refinement tests failed.")

if __name__ == "__main__":
    test_refinement()

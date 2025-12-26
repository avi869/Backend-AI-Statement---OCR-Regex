
import re
import unittest

# Import the function to be tested
# We will need to slightly modify the original script to make the function importable or just paste the improved version here for testing first.
# For now, let's redefine the parse logic here to test it rapidly, then backport to the main script.


import sys
import os

# Add script dir to sys.path to ensure import works
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bank_statement_ocr import parse_transactions


class TestOCRParser(unittest.TestCase):
    def test_parsing(self):
        # Mock text simulating OCR output based on the screenshot provided
        # Note: OCR often puts everything on one line or breaks lines unpredictably.
        # We assume psm 6 gives roughly linear text.
        
        mock_ocr_output = """
        Oct 23, 2025
        06:12 PM
        Paid to RAKESH KUMAR
        Transaction ID T25102318
        DEBIT
        ₹40
        Oct 21, 2025
        07:44 PM
        Mobile recharged 8986721145
        Transaction ID NX2510211
        DEBIT
        ₹150.14
        Oct 18, 2025
        Paid to Flipkart
        DEBIT ₹756
        Oct 01, 2025
        Received from ANAM ANSARI
        CREDIT
        ₹300
        """
        
        results = parse_transactions(mock_ocr_output)
        
        # Print for visual verification
        print("\n--- TEST RESULTS ---")
        for t in results:
            print(t)
            
        # Assertions
        self.assertEqual(len(results), 4)
        
        # Check first item
        self.assertEqual(results[0]['Date'], 'Oct 23, 2025')
        self.assertEqual(results[0]['Amount'], '40')
        self.assertEqual(results[0]['Type'], 'DEBIT')
        self.assertTrue('Paid to RAKESH KUMAR' in results[0]['Description'])

        # Check the 'Mobile recharged' item (The one that was failing)
        self.assertEqual(results[1]['Date'], 'Oct 21, 2025')
        self.assertEqual(results[1]['Amount'], '150.14')
        self.assertEqual(results[1]['Type'], 'DEBIT')
        self.assertTrue('Mobile recharged' in results[1]['Description'])
        self.assertTrue('8986721145' in results[1]['Description'])

if __name__ == '__main__':
    unittest.main()

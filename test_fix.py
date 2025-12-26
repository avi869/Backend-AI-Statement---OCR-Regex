
import unittest
import sys
import os

# Add script dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bank_statement_ocr import parse_transactions

class TestOCRParserRefined(unittest.TestCase):
    def test_parsing_missing_amount(self):
        # Mock text based on the user's actual problematic output
        mock_ocr_output = """
        Oct 23, 2025
        Paid to RAKESH KUMAR DEBIT 740
        Oct 18, 2025
        Paid to Flipkart DEBIT 2756
        Oct 05, 2025
        Mobile recharged 6201476226 DEBIT 7304.33
        Sep 30, 2025
        Received from Mr Abhishek Kumar Jha CREDIT
        """
        
        results = parse_transactions(mock_ocr_output)
        
        # Verify result count
        self.assertEqual(len(results), 4)

        # 1. Check Split Logic
        # It should correctly identify Description vs Amount using DEBIT/CREDIT
        
        # Item 1
        self.assertEqual(results[0]['Date'], 'Oct 23, 2025')
        self.assertEqual(results[0]['Type'], 'DEBIT')
        # Description should NOT contain DEBIT ...
        self.assertIn('Paid to RAKESH KUMAR', results[0]['Description']) 
        self.assertNotIn('DEBIT', results[0]['Description'])
        # Amount should be captured (even if it is 740 due to OCR noise)
        self.assertEqual(results[0]['Amount'], '740')

        # Item 2
        self.assertEqual(results[1]['Amount'], '2756')
        
        # Item 3 (Mobile recharged)
        self.assertIn('Mobile recharged 6201476226', results[2]['Description'])
        self.assertEqual(results[2]['Amount'], '7304.33')

if __name__ == '__main__':
    unittest.main()

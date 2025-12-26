
import unittest
import sys
import os

# Add script dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bank_statement_ocr import parse_transactions

class TestOCRParser(unittest.TestCase):
    def test_parsing(self):
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
        """
        
        results = parse_transactions(mock_ocr_output)
        
        self.assertEqual(len(results), 3)
        self.assertTrue('Paid to RAKESH KUMAR' in results[0]['Description'])
        self.assertTrue('Mobile recharged' in results[1]['Description']) # Key fix
        self.assertEqual(results[1]['Amount'], '150.14')

if __name__ == '__main__':
    unittest.main()

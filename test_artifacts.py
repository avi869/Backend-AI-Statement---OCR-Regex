
import unittest
import sys
import os

# Add script dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bank_statement_ocr import parse_transactions

class TestOCRFixArtifacts(unittest.TestCase):
    def test_artifact_removal(self):
        # Mock text with known artifacts
        mock_ocr_output = """
        Oct 23, 2025
        Paid to RAKESH KUMAR DEBIT 740
        Oct 21, 2025
        Mobile recharged DEBIT 7304.33
        Oct 18, 2025
        Paid to Flipkart DEBIT 2756
        """
        
        results = parse_transactions(mock_ocr_output)
        
        self.assertEqual(len(results), 3)
        
        # Expectation: 740 -> 40
        self.assertEqual(results[0]['Amount'], '40')
        
        # Expectation: 7304.33 -> 304.33
        self.assertEqual(results[1]['Amount'], '304.33')
        
        # Expectation: 2756 -> 756 (Assuming 2 is the artifact for ₹ here based on user data)
        # Wait, if 2756 -> 756, that implies 2 is the artifact.
        self.assertEqual(results[2]['Amount'], '756')

if __name__ == '__main__':
    unittest.main()

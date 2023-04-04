import unittest
import io
import sys
import os
from redaction_script import main

class TestMain(unittest.TestCase):

    def setUp(self):
        self.arguments_test = [
            "--input", "test_file.txt",
            "--names",
            "--output", "test_output",
            "--stats", "test_stats.txt"
        ]
        self.input_text = "This is a test text that contains some names like John Doe and some dates like 12/31/2022."

    def test_main(self):
        # Redirect stdout to a buffer
        captured_output = io.StringIO()
        sys.stdout = captured_output

        # Create a test input file
        with open("test_file.txt", "w") as f:
            f.write(self.input_text)

        # Call the main function with test arguments
        main(self.arguments_test)

        # Reset stdout
        sys.stdout = sys.__stdout__

        # Check that output file was created
        self.assertTrue(os.path.exists("test_output/test_file.txt"))

        # Check that stats file was created
        self.assertTrue(os.path.exists("test_stats.txt"))

        # Check that output file contains redacted names and dates
        with open("test_output/test_file.txt", "r") as f:
            output_text = f.read()
            self.assertIn("███ is a test text that contains some names like ████ ███ and some dates like ██/██/████.", output_text)

        # Check that stats file contains statistics
        with open("test_stats.txt", "r") as f:
            stats_text = f.read()
            self.assertIn("Statistics from redaction process for test_file.txt:", stats_text)

        # Clean up test files
        os.remove("test_file.txt")
        os.remove("test_stats.txt")
        os.remove("test_output/test_file.txt")

if __name__ == '__main__':
    unittest.main()

import unittest
import requests
from pathlib import Path

class TestArchiveUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Define the endpoint and path to the test file
        cls.url = 'http://127.0.0.1:8001/archive/'
        cls.file_path = '/home/fortex/Загрузки/cloud.py'
        
        # Ensure the file exists
        if not Path(cls.file_path).is_file():
            raise FileNotFoundError(f"Test file not found at {cls.file_path}")

    def test_archive_upload(self):
        # Open the file for the POST request
        with open(self.file_path, 'rb') as file:
            files = {"files": file}
            response = requests.post(self.url, files=files)
            
            # Assertions to check if the response was successful and returned expected data
            self.assertEqual(response.status_code, 200, "Expected status code 200")
            response_data = response.json()
            self.assertIn('archive_filename', response_data, "Response JSON should contain 'archive_filename'")
            self.assertIn('archive_path', response_data, "Response JSON should contain 'archive_path'")
            
            print(response_data)

if __name__ == '__main__':
    unittest.main()

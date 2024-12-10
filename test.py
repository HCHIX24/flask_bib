import unittest
from app import create_app  # Import your Flask app factory

class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        # Create a test client for the app
        self.app = create_app()
        self.client = self.app.test_client()

    def test_hello_endpoint(self):
        # Make a GET request to the /hello endpoint
        response = self.client.get('/hello')
        
        # Check the response status code
        self.assertEqual(response.status_code, 200)
        
        # Check the response JSON data
        self.assertEqual(response.json, {"message": "Hello, World!"})

    def tearDown(self):
        # Clean up resources after tests (if necessary)
        pass

if __name__ == '__main__':
    unittest.main()

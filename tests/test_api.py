import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import json

# Ensure api directory is in import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

# Avoid starting real debug server during imports
os.environ['FLASK_ENV'] = 'testing'

from index import app

class TestAPI(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'mindease-wellbeing-coach')
        self.assertIn('ai_enabled', data)

    def test_get_wellbeing_example(self):
        response = self.app.get('/api/wellbeing-example')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('empathy_statement', data)
        self.assertIn('insights', data)
        self.assertIn('coping_strategies', data)

    @patch('index.advisor')
    def test_analyze_wellbeing_success(self, mock_advisor):
        mock_advisor.analyze_wellbeing.return_value = {
            "empathy_statement": "Mock empathy",
            "insights": "Mock insights",
            "coping_strategies": ["Strategy 1"],
            "hobby_integration": "Mock hobby",
            "custom_affirmation": "Mock affirmation",
            "suggested_actions": ["Action 1"]
        }
        
        payload = {
            "mood": "Stressed",
            "exam": "NEET",
            "triggers": ["Lack of sleep"],
            "hobbies": ["Music"],
            "journal": "Feeling tired"
        }
        
        response = self.app.post(
            '/api/analyze-wellbeing',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['empathy_statement'], 'Mock empathy')
        mock_advisor.analyze_wellbeing.assert_called_once_with(
            "Stressed", "NEET", ["Lack of sleep"], ["Music"], "Feeling tired"
        )

    def test_analyze_wellbeing_missing_fields(self):
        payload = {
            "triggers": ["Lack of sleep"],
            "hobbies": ["Music"]
        }
        
        response = self.app.post(
            '/api/analyze-wellbeing',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('error', data)

    def test_security_headers_present(self):
        # Even on simple requests, security headers should be present
        response = self.app.get('/health')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
        self.assertIsNotNone(response.headers.get('Content-Security-Policy'))

    @patch('index.send_from_directory')
    def test_serve_static_index(self, mock_send):
        mock_send.return_value = app.response_class("Mock index", status=200)
        
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), "Mock index")

    @patch('index.send_from_directory')
    def test_serve_static_index_error(self, mock_send):
        mock_send.side_effect = Exception("File read error")
        response = self.app.get('/')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('error', data)
        
    @patch('index.send_from_directory')
    def test_serve_static_assets_caching(self, mock_send):
        mock_send.return_value = app.response_class("Mock Image Data", status=200)
        
        response = self.app.get('/assets/naruto.png')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cache-Control', response.headers)
        self.assertEqual(response.headers['Cache-Control'], 'public, max-age=31536000, immutable')

    @patch('index.advisor')
    def test_translate_wellbeing_success(self, mock_advisor):
        mock_advisor.translate_wellbeing.return_value = {
            "empathy_statement": "Mock empathy in Hindi"
        }
        
        payload = {"empathy_statement": "Mock empathy"}
        response = self.app.post(
            '/api/translate-wellbeing',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['empathy_statement'], 'Mock empathy in Hindi')
        mock_advisor.translate_wellbeing.assert_called_once_with(payload)

    def test_translate_wellbeing_missing_payload(self):
        response = self.app.post(
            '/api/translate-wellbeing',
            data=None,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    @patch('index.send_from_directory')
    def test_serve_static_css_js_caching(self, mock_send):
        mock_send.return_value = app.response_class("Mock JS Data", status=200)
        
        response = self.app.get('/script.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cache-Control', response.headers)
        self.assertEqual(response.headers['Cache-Control'], 'public, max-age=86400')

    @patch('index.advisor')
    def test_analyze_wellbeing_internal_error(self, mock_advisor):
        mock_advisor.analyze_wellbeing.side_effect = Exception("API failure")
        payload = {
            "mood": "Stressed",
            "exam": "NEET"
        }
        response = self.app.post(
            '/api/analyze-wellbeing',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('error', data)

    @patch('index.advisor')
    def test_translate_wellbeing_internal_error(self, mock_advisor):
        mock_advisor.translate_wellbeing.side_effect = Exception("Translate failure")
        payload = {"empathy_statement": "Hello"}
        response = self.app.post(
            '/api/translate-wellbeing',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('error', data)

    def test_serve_static_other_file_direct(self):
        with app.test_request_context():
            with patch('index.send_from_directory') as mock_send:
                mock_send.return_value = app.response_class("Mock Plain Data", status=200)
                from index import serve_static
                response = serve_static('readme.md')
                self.assertEqual(response.status_code, 200)
                self.assertIn('Cache-Control', response.headers)
                self.assertEqual(response.headers['Cache-Control'], 'public, max-age=3600')

    def test_serve_static_fallback_index_direct(self):
        with app.test_request_context():
            with patch('index.send_from_directory') as mock_send:
                mock_send.side_effect = [Exception("File not found"), app.response_class("Mock Index Data", status=200)]
                from index import serve_static
                response = serve_static('nonexistent-file.html')
                self.assertEqual(response.status_code, 200)
                self.assertIn('Cache-Control', response.headers)
                self.assertEqual(response.headers['Cache-Control'], 'no-cache, no-store, must-revalidate')

    def test_serve_static_complete_failure_direct(self):
        with app.test_request_context():
            with patch('index.send_from_directory') as mock_send:
                mock_send.side_effect = Exception("General error")
                from index import serve_static
                res, status_code = serve_static('critical-failure.html')
                self.assertEqual(status_code, 404)
                data = json.loads(res.data.decode('utf-8'))
                self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()

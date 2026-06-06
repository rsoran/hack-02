import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Ensure api directory is in import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

from wellbeing_advisor import WellbeingAdvisor

class TestWellbeingAdvisor(unittest.TestCase):
    
    def setUp(self):
        # Prevent WellbeingAdvisor from configuring real API key in tests
        self.patcher = patch('wellbeing_advisor.genai')
        self.mock_genai = self.patcher.start()
        
        # Mock class variables if needed
        self.advisor = WellbeingAdvisor()
        
    def tearDown(self):
        self.patcher.stop()

    def test_advisor_initialization_no_key(self):
        # Test default fallback state when key is missing
        with patch.dict(os.environ, {}, clear=True):
            advisor = WellbeingAdvisor()
            self.assertIsNone(advisor.model)

    def test_build_prompt(self):
        prompt = self.advisor._build_prompt(
            mood="Anxious",
            exam="JEE",
            triggers=["Backlog"],
            hobbies=["Music"],
            journal="Worried"
        )
        self.assertIn("Anxious", prompt)
        self.assertIn("JEE", prompt)
        self.assertIn("Backlog", prompt)
        self.assertIn("Music", prompt)
        self.assertIn("Worried", prompt)

    def test_generate_fallback_response(self):
        fallback = self.advisor._generate_fallback_response(
            mood="Burned Out",
            exam="NEET",
            triggers=["Mock Scores"],
            hobbies=["Art"]
        )
        self.assertIn("empathy_statement", fallback)
        self.assertIn("insights", fallback)
        self.assertIn("coping_strategies", fallback)
        self.assertIn("hobby_integration", fallback)
        self.assertIn("custom_affirmation", fallback)
        self.assertIn("suggested_actions", fallback)
        
        self.assertIn("NEET", fallback["empathy_statement"])
        self.assertIn("burned out", fallback["empathy_statement"])
        self.assertIn("Art", fallback["hobby_integration"])

    def test_parse_response_valid_json(self):
        valid_json_text = '{"empathy_statement": "I feel you", "insights": "Stress", "coping_strategies": ["Breathe"], "hobby_integration": "Do art", "custom_affirmation": "I can", "suggested_actions": ["Rest"]}'
        parsed = self.advisor._parse_response(valid_json_text, "Anxious", "JEE", [], [])
        self.assertEqual(parsed["empathy_statement"], "I feel you")
        self.assertEqual(parsed["insights"], "Stress")

    def test_parse_response_markdown_json(self):
        markdown_json_text = '```json\n{"empathy_statement": "I feel you", "insights": "Stress", "coping_strategies": ["Breathe"], "hobby_integration": "Do art", "custom_affirmation": "I can", "suggested_actions": ["Rest"]}\n```'
        parsed = self.advisor._parse_response(markdown_json_text, "Anxious", "JEE", [], [])
        self.assertEqual(parsed["empathy_statement"], "I feel you")

    def test_parse_response_invalid_json_triggers_fallback(self):
        invalid_json_text = 'invalid json data'
        parsed = self.advisor._parse_response(invalid_json_text, "Anxious", "JEE", ["Syllabus"], ["Music"])
        self.assertIn("JEE", parsed["empathy_statement"])
        self.assertIn("Syllabus", parsed["empathy_statement"])

    @patch('wellbeing_advisor.WellbeingAdvisor._parse_response')
    def test_analyze_wellbeing_with_model(self, mock_parse):
        # Setup mock model
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "mocked text response"
        mock_model.generate_content.return_value = mock_response
        self.advisor.model = mock_model
        
        mock_parse.return_value = {"status": "mocked_parse_success"}
        
        result = self.advisor.analyze_wellbeing("Anxious", "JEE", [], [], "Journal")
        
        mock_model.generate_content.assert_called_once()
        mock_parse.assert_called_once_with("mocked text response", "Anxious", "JEE", [], [])
        self.assertEqual(result["status"], "mocked_parse_success")

    def test_analyze_wellbeing_exception_triggers_fallback(self):
        # Setup mock model that raises error
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API connection error")
        self.advisor.model = mock_model
        
        result = self.advisor.analyze_wellbeing("Anxious", "JEE", ["Pressure"], ["Music"], "Journal")
        self.assertIn("JEE", result["empathy_statement"])
        self.assertIn("Pressure", result["empathy_statement"])

    def test_generate_fallback_translation(self):
        plan_json = {"empathy_statement": "Hello", "insights": "Stress"}
        fallback = self.advisor._generate_fallback_translation(plan_json)
        self.assertIn("empathy_statement", fallback)
        self.assertIn("तनाव", fallback["insights"])
        self.assertIn("परीक्षा की तैयारी", fallback["empathy_statement"])

    @patch('wellbeing_advisor.WellbeingAdvisor._parse_response')
    def test_translate_wellbeing_with_model(self, mock_parse):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "mocked translated text"
        mock_model.generate_content.return_value = mock_response
        self.advisor.model = mock_model
        
        mock_parse.return_value = {"empathy_statement": "नमस्ते"}
        
        result = self.advisor.translate_wellbeing({"empathy_statement": "Hello"})
        mock_model.generate_content.assert_called_once()
        self.assertEqual(result["empathy_statement"], "नमस्ते")

    def test_translate_wellbeing_fallback_on_exception(self):
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API error")
        self.advisor.model = mock_model
        
        result = self.advisor.translate_wellbeing({"empathy_statement": "Hello"})
        self.assertIn("परीक्षा की तैयारी", result["empathy_statement"])

if __name__ == '__main__':
    unittest.main()

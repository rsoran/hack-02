import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Add current api folder to path for absolute imports inside Vercel
sys.path.append(os.path.dirname(__file__))

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from config import config
from wellbeing_advisor import WellbeingAdvisor

# Initialize Flask app
static_folder = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app = Flask(__name__, static_folder=static_folder, static_url_path='')

# Load config
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(config_name, config['default']))

CORS(app)

# Initialize advisor
advisor = WellbeingAdvisor()

@app.route('/', methods=['GET'])
def index():
    """Serve index.html"""
    try:
        return send_from_directory(static_folder, 'index.html')
    except Exception as e:
        print(f"Error serving index.html: {e}")
        return jsonify({'error': 'Frontend not found'}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'mindease-wellbeing-coach',
        'ai_enabled': advisor.model is not None
    }), 200

@app.route('/api/analyze-wellbeing', methods=['POST'])
def analyze_wellbeing():
    """
    Analyze student wellbeing and generate copings/recommendations.
    Expects:
    {
      "mood": "Stressed",
      "exam": "JEE",
      "triggers": ["Mock Test Scores"],
      "hobbies": ["Music"],
      "journal": "Text"
    }
    """
    try:
        data = request.get_json()
        if not data or 'mood' not in data or 'exam' not in data:
            return jsonify({'error': 'Missing required fields: mood, exam'}), 400
            
        mood = data.get('mood')
        exam = data.get('exam')
        triggers = data.get('triggers', [])
        hobbies = data.get('hobbies', [])
        journal = data.get('journal', '')
        
        result = advisor.analyze_wellbeing(mood, exam, triggers, hobbies, journal)
        return jsonify(result), 200
    except Exception as e:
        print(f"Exception in analyze_wellbeing: {e}")
        return jsonify({'error': 'Internal server error during analysis'}), 500

@app.route('/api/wellbeing-example', methods=['GET'])
def get_wellbeing_example():
    """Return an example response payload"""
    example = {
        "empathy_statement": "Preparing for exams is a challenging phase, and feeling anxious or stressed is completely valid.",
        "insights": "Under extreme test-taking stress, your brain defaults to a 'fight or flight' mode, amplifying fear of failure.",
        "coping_strategies": [
            "Use the 4-7-8 deep breathing technique to reset your nervous system during anxiety peaks.",
            "Break your backlog into atomic, 25-minute tasks to reduce starting friction."
        ],
        "hobby_integration": "Taking structured 15-minute breaks to pursue your hobbies is a high-value active recovery method.",
        "custom_affirmation": "My exam preparation does not define my self-worth. I am learning and growing every day.",
        "suggested_actions": [
            "Complete 3 cycles of Box Breathing.",
            "Write down your single highest study priority for today and ignore the rest."
        ]
    }
    return jsonify(example), 200

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve static files"""
    try:
        return send_from_directory(static_folder, path)
    except Exception:
        try:
            return send_from_directory(static_folder, 'index.html')
        except Exception:
            return jsonify({'error': 'Endpoint not found'}), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

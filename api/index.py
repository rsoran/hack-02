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

# Harden CORS to secure API routes and restrict credentials
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

# Initialize advisor
advisor = WellbeingAdvisor()

@app.after_request
def add_security_headers(response):
    """Add standard security headers and Cache-Control rules to responses"""
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Content Security Policy (CSP) tailored for the styling and font dependencies of the frontend
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    response.headers['Content-Security-Policy'] = csp_policy
    
    # Apply caching policies based on request path
    path = request.path
    if path.startswith('/assets/') or path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff2', '.woff', '.ttf')):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    elif path.endswith(('.css', '.js')):
        response.headers['Cache-Control'] = 'public, max-age=86400'
    elif path == '/' or path == '/index.html':
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
    return response

@app.route('/', methods=['GET'])
def index():
    """Serve index.html with cache-busting headers"""
    try:
        response = send_from_directory(static_folder, 'index.html')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
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
    """Serve static files with appropriate cache control rules"""
    try:
        response = send_from_directory(static_folder, path)
        # Apply caching policies for asset optimization
        if path.startswith('assets/') or path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff2', '.woff', '.ttf')):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        elif path.endswith(('.css', '.js')):
            response.headers['Cache-Control'] = 'public, max-age=86400' # 1 day for styles/scripts
        else:
            response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
    except Exception:
        try:
            response = send_from_directory(static_folder, 'index.html')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            return response
        except Exception:
            return jsonify({'error': 'Endpoint not found'}), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

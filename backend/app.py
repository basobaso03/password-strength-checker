"""
Flask Backend API for Password Strength Checker
Provides REST endpoints for password validation and analysis.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from checker import PasswordStrengthChecker
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize password checker
checker = PasswordStrengthChecker()


@app.route('/api/check', methods=['POST'])
def check_password():
    """
    Check password strength via POST request.
    
    Request body:
        {
            "password": "user_password"
        }
    
    Response:
        {
            "strength": "strong|medium|weak",
            "score": 0-100,
            "feedback": "Human readable feedback",
            "criteria": {...},
            "suggestions": [...],
            "entropy": 0-100
        }
    """
    try:
        # Get password from request
        data = request.get_json()
        
        if not data or 'password' not in data:
            return jsonify({
                'error': 'Password field is required',
                'status': 'error'
            }), 400
        
        password = data.get('password', '')
        
        # Validate input
        if not isinstance(password, str):
            return jsonify({
                'error': 'Password must be a string',
                'status': 'error'
            }), 400
        
        if len(password) > 500:
            return jsonify({
                'error': 'Password exceeds maximum length (500 characters)',
                'status': 'error'
            }), 400
        
        # Check password strength
        result = checker.check_password(password)
        
        # Add metadata
        result['status'] = 'success'
        result['timestamp'] = datetime.now().isoformat()
        
        logger.info(f"Password checked - Strength: {result['strength']}, Score: {result['score']}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error checking password: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for API status."""
    return jsonify({
        'status': 'healthy',
        'service': 'Password Strength Checker API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/info', methods=['GET'])
def get_info():
    """Get information about the password checker."""
    return jsonify({
        'name': 'Password Strength Checker',
        'version': '1.0.0',
        'description': 'Analyzes password strength using entropy principles and security criteria',
        'criteria': [
            'Minimum length (8+ characters recommended)',
            'Uppercase letters (A-Z)',
            'Lowercase letters (a-z)',
            'Numbers (0-9)',
            'Special symbols (!@#$%^&*)',
            'No repeated characters (3+ consecutive)',
            'No sequential patterns (abc, 123, qwerty)'
        ],
        'endpoints': {
            '/api/check': 'POST - Check password strength',
            '/api/health': 'GET - Health check',
            '/api/info': 'GET - API information'
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500


if __name__ == '__main__':
    # Development server - use with caution in production
    app.run(debug=True, host='0.0.0.0', port=5000)

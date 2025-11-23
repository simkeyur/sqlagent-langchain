"""Flask application for Employee Database Query Interface."""

import os
import json
import logging
from flask import Flask, render_template, request, jsonify
from sql_agent import query_database
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Settings storage (in production, use database)
SETTINGS_FILE = 'settings.json'


def load_settings():
    """Load settings from file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {"api_key": ""}


def save_settings(settings):
    """Save settings to file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)


def require_api_key(f):
    """Decorator to check if API key is configured."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        settings = load_settings()
        if not settings.get("api_key"):
            return jsonify({"error": "API key not configured. Please configure in settings."}), 400
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Serve the main page."""
    logger.info("📄 Index page requested")
    return render_template('index.html')


@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Handle settings GET and POST requests."""
    if request.method == 'GET':
        logger.info("⚙️ Settings GET request")
        current_settings = load_settings()
        # Don't send the full API key to frontend for security
        return jsonify({
            "api_key_configured": bool(current_settings.get("api_key"))
        })
    
    elif request.method == 'POST':
        logger.info("⚙️ Settings POST request received")
        data = request.get_json()
        api_key = data.get("api_key", "").strip()
        
        if not api_key:
            logger.warning("⚠️ API key validation failed: empty key")
            return jsonify({"error": "API key cannot be empty"}), 400
        
        settings_data = {"api_key": api_key}
        save_settings(settings_data)
        logger.info("✅ API key configured successfully")
        
        return jsonify({"message": "Settings saved successfully"})


@app.route('/api/query', methods=['POST'])
@require_api_key
def query():
    """Handle natural language queries."""
    data = request.get_json()
    user_query = data.get("query", "").strip()
    
    logger.info(f"🔎 Query received from client: '{user_query}'")
    
    if not user_query:
        logger.warning("⚠️ Query validation failed: empty query")
        return jsonify({"error": "Query cannot be empty"}), 400
    
    settings = load_settings()
    api_key = settings.get("api_key")
    
    logger.info(f"🔐 Using configured API key for query execution")
    
    # Execute query using SQL agent
    result = query_database(user_query, api_key)
    
    if result["success"]:
        logger.info(f"✅ Query executed successfully, formatted={result.get('formatted')}")
        return jsonify({
            "success": True,
            "result": result["result"]
        })
    else:
        logger.error(f"❌ Query execution failed: {result['error']}")
        return jsonify({
            "success": False,
            "error": result["error"]
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    logger.info("💚 Health check requested")
    settings = load_settings()
    return jsonify({
        "status": "ok",
        "api_key_configured": bool(settings.get("api_key"))
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

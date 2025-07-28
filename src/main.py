import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO
from src.models.user import db
from src.models.campaign import Campaign
from src.models.company import Company
from src.models.person import Person
from src.models.context_snippet import ContextSnippet
from src.models.search_log import SearchLog
from src.routes.user import user_bp
from src.routes.people import people_bp
from src.routes.research import research_bp
from src.routes.campaigns import campaigns_bp
from src.routes.search import search_bp
from src.routes.websocket_routes import websocket_routes_bp
from src.services.websocket_service import init_websocket_service

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app, origins='*')

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(people_bp, url_prefix='/api')
app.register_blueprint(research_bp, url_prefix='/api')
app.register_blueprint(campaigns_bp, url_prefix='/api')
app.register_blueprint(search_bp, url_prefix='/api')
app.register_blueprint(websocket_routes_bp, url_prefix='/api')

# Initialize WebSocket service
websocket_service = init_websocket_service(socketio)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables and seed data
with app.app_context():
    db.create_all()
    
    # Check if data already exists
    if db.session.query(Campaign).count() == 0:
        from src.seed_data import seed_database
        seed_database()

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': '2025-07-28T12:00:00Z',
        'version': '2.0.0',
        'database': 'connected',
        'redis': 'not_configured'
    }

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

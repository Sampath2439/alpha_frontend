from flask import Blueprint, request, jsonify
from src.services.websocket_service import get_websocket_service
import uuid

websocket_routes_bp = Blueprint('websocket_routes', __name__)

@websocket_routes_bp.route('/research/start-session', methods=['POST'])
def start_research_session():
    """Start a new research session with WebSocket progress tracking"""
    try:
        data = request.get_json()
        person_id = data.get('person_id')
        person_name = data.get('person_name', 'Unknown Person')
        
        if not person_id:
            return jsonify({
                'success': False,
                'error': 'person_id is required'
            }), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Get WebSocket service
        ws_service = get_websocket_service()
        if not ws_service:
            return jsonify({
                'success': False,
                'error': 'WebSocket service not available'
            }), 500
        
        # Start the research session
        ws_service.start_research_session(session_id, person_id, person_name)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Research session started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@websocket_routes_bp.route('/research/session/<session_id>/progress', methods=['GET'])
def get_session_progress(session_id):
    """Get current progress for a research session"""
    try:
        ws_service = get_websocket_service()
        if not ws_service:
            return jsonify({
                'success': False,
                'error': 'WebSocket service not available'
            }), 500
        
        progress = ws_service.get_session_progress(session_id)
        if not progress:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'progress': progress
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@websocket_routes_bp.route('/research/session/<session_id>/complete', methods=['POST'])
def complete_research_session(session_id):
    """Mark a research session as completed"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        ws_service = get_websocket_service()
        if not ws_service:
            return jsonify({
                'success': False,
                'error': 'WebSocket service not available'
            }), 500
        
        ws_service.complete_research(session_id, results)
        
        return jsonify({
            'success': True,
            'message': 'Research session completed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@websocket_routes_bp.route('/research/session/<session_id>/error', methods=['POST'])
def error_research_session(session_id):
    """Mark a research session as failed"""
    try:
        data = request.get_json()
        error_message = data.get('error_message', 'Unknown error occurred')
        
        ws_service = get_websocket_service()
        if not ws_service:
            return jsonify({
                'success': False,
                'error': 'WebSocket service not available'
            }), 500
        
        ws_service.error_research(session_id, error_message)
        
        return jsonify({
            'success': True,
            'message': 'Research session marked as failed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@websocket_routes_bp.route('/research/session/<session_id>/cleanup', methods=['DELETE'])
def cleanup_research_session(session_id):
    """Clean up a completed research session"""
    try:
        ws_service = get_websocket_service()
        if not ws_service:
            return jsonify({
                'success': False,
                'error': 'WebSocket service not available'
            }), 500
        
        ws_service.cleanup_session(session_id)
        
        return jsonify({
            'success': True,
            'message': 'Research session cleaned up'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


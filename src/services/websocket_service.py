from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from datetime import datetime
import json
import threading
import time

class WebSocketService:
    def __init__(self, socketio):
        self.socketio = socketio
        self.active_sessions = {}
        self.progress_data = {}
    
    def init_handlers(self):
        """Initialize WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            print(f"Client connected: {request.sid}")
            emit('connected', {'status': 'Connected to Alpha Platform'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            print(f"Client disconnected: {request.sid}")
            # Clean up any active sessions for this client
            if request.sid in self.active_sessions:
                del self.active_sessions[request.sid]
        
        @self.socketio.on('join_research_session')
        def handle_join_research_session(data):
            """Join a research session room for progress updates"""
            session_id = data.get('session_id')
            if session_id:
                join_room(session_id)
                self.active_sessions[request.sid] = session_id
                emit('joined_session', {
                    'session_id': session_id,
                    'status': 'Joined research session'
                })
        
        @self.socketio.on('leave_research_session')
        def handle_leave_research_session(data):
            """Leave a research session room"""
            session_id = data.get('session_id')
            if session_id:
                leave_room(session_id)
                if request.sid in self.active_sessions:
                    del self.active_sessions[request.sid]
                emit('left_session', {
                    'session_id': session_id,
                    'status': 'Left research session'
                })
        
        @self.socketio.on('get_progress')
        def handle_get_progress(data):
            """Get current progress for a session"""
            session_id = data.get('session_id')
            if session_id and session_id in self.progress_data:
                emit('progress_update', self.progress_data[session_id])
    
    def start_research_session(self, session_id, person_id, person_name):
        """Start a new research session"""
        self.progress_data[session_id] = {
            'session_id': session_id,
            'person_id': person_id,
            'person_name': person_name,
            'status': 'starting',
            'progress': 0,
            'current_step': 'Initializing research...',
            'steps_completed': 0,
            'total_steps': 5,
            'start_time': datetime.utcnow().isoformat(),
            'estimated_completion': None,
            'results': []
        }
        
        # Emit initial status
        self.socketio.emit('research_started', self.progress_data[session_id], room=session_id)
        
        # Start the research process in a separate thread
        thread = threading.Thread(target=self._simulate_research_process, args=(session_id,))
        thread.daemon = True
        thread.start()
    
    def _simulate_research_process(self, session_id):
        """Simulate the research process with progress updates"""
        if session_id not in self.progress_data:
            return
        
        steps = [
            {'step': 'Searching LinkedIn profiles...', 'duration': 2},
            {'step': 'Analyzing company information...', 'duration': 3},
            {'step': 'Gathering social media data...', 'duration': 2},
            {'step': 'Processing competitive intelligence...', 'duration': 4},
            {'step': 'Finalizing research report...', 'duration': 1}
        ]
        
        for i, step_info in enumerate(steps):
            if session_id not in self.progress_data:
                break
            
            # Update progress
            self.progress_data[session_id].update({
                'status': 'in_progress',
                'progress': int((i / len(steps)) * 100),
                'current_step': step_info['step'],
                'steps_completed': i,
                'estimated_completion': datetime.utcnow().isoformat()
            })
            
            # Emit progress update
            self.socketio.emit('progress_update', self.progress_data[session_id], room=session_id)
            
            # Simulate work
            time.sleep(step_info['duration'])
            
            # Add some results
            if i == 1:  # Company analysis step
                self.progress_data[session_id]['results'].append({
                    'type': 'company_info',
                    'data': {
                        'name': 'TechCorp Inc.',
                        'industry': 'Technology',
                        'employees': '500-1000',
                        'revenue': '$50M-$100M'
                    }
                })
            elif i == 3:  # Competitive intelligence step
                self.progress_data[session_id]['results'].append({
                    'type': 'competitive_intel',
                    'data': {
                        'competitors': ['CompetitorA', 'CompetitorB'],
                        'market_position': 'Strong',
                        'key_differentiators': ['Innovation', 'Customer Service']
                    }
                })
        
        # Complete the research
        if session_id in self.progress_data:
            self.progress_data[session_id].update({
                'status': 'completed',
                'progress': 100,
                'current_step': 'Research completed successfully!',
                'steps_completed': len(steps),
                'completion_time': datetime.utcnow().isoformat()
            })
            
            # Emit completion
            self.socketio.emit('research_completed', self.progress_data[session_id], room=session_id)
    
    def update_progress(self, session_id, progress_data):
        """Update progress for a specific session"""
        if session_id in self.progress_data:
            self.progress_data[session_id].update(progress_data)
            self.socketio.emit('progress_update', self.progress_data[session_id], room=session_id)
    
    def complete_research(self, session_id, results):
        """Mark research as completed with results"""
        if session_id in self.progress_data:
            self.progress_data[session_id].update({
                'status': 'completed',
                'progress': 100,
                'current_step': 'Research completed successfully!',
                'completion_time': datetime.utcnow().isoformat(),
                'results': results
            })
            
            self.socketio.emit('research_completed', self.progress_data[session_id], room=session_id)
    
    def error_research(self, session_id, error_message):
        """Mark research as failed with error"""
        if session_id in self.progress_data:
            self.progress_data[session_id].update({
                'status': 'error',
                'current_step': f'Error: {error_message}',
                'error_time': datetime.utcnow().isoformat(),
                'error_message': error_message
            })
            
            self.socketio.emit('research_error', self.progress_data[session_id], room=session_id)
    
    def get_session_progress(self, session_id):
        """Get current progress for a session"""
        return self.progress_data.get(session_id)
    
    def cleanup_session(self, session_id):
        """Clean up completed session data"""
        if session_id in self.progress_data:
            del self.progress_data[session_id]

# Global WebSocket service instance
websocket_service = None

def init_websocket_service(socketio):
    """Initialize the global WebSocket service"""
    global websocket_service
    websocket_service = WebSocketService(socketio)
    websocket_service.init_handlers()
    return websocket_service

def get_websocket_service():
    """Get the global WebSocket service instance"""
    return websocket_service


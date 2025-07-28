import uuid
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class SearchLog(db.Model):
    __tablename__ = 'search_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    context_snippet_id = db.Column(db.String(36), db.ForeignKey('context_snippets.id', ondelete='CASCADE'), nullable=False)
    iteration = db.Column(db.Integer)
    query = db.Column(db.Text)
    top_results = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def get_top_results(self):
        """Get top results as Python dict"""
        try:
            return json.loads(self.top_results) if self.top_results else {}
        except json.JSONDecodeError:
            return {}
    
    def set_top_results(self, results):
        """Set top results from Python dict"""
        self.top_results = json.dumps(results) if results else '{}'
    
    def to_dict(self):
        return {
            'id': self.id,
            'context_snippet_id': self.context_snippet_id,
            'iteration': self.iteration,
            'query': self.query,
            'top_results': self.get_top_results(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


import uuid
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class ContextSnippet(db.Model):
    __tablename__ = 'context_snippets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = db.Column(db.String(50), nullable=False)  # 'company' or 'person'
    entity_id = db.Column(db.String(36), nullable=False)
    snippet_type = db.Column(db.String(50), default='research')
    payload = db.Column(db.Text, nullable=False)  # JSON string
    source_urls = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign key relationships
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'))
    person_id = db.Column(db.String(36), db.ForeignKey('people.id', ondelete='CASCADE'))
    
    # Relationships
    search_logs = db.relationship('SearchLog', backref='context_snippet', cascade='all, delete-orphan')
    
    def get_payload(self):
        """Get payload as Python dict"""
        try:
            return json.loads(self.payload) if self.payload else {}
        except json.JSONDecodeError:
            return {}
    
    def set_payload(self, data):
        """Set payload from Python dict"""
        self.payload = json.dumps(data) if data else '{}'
    
    def get_source_urls(self):
        """Get source URLs as Python list"""
        try:
            return json.loads(self.source_urls) if self.source_urls else []
        except json.JSONDecodeError:
            return []
    
    def set_source_urls(self, urls):
        """Set source URLs from Python list"""
        self.source_urls = json.dumps(urls) if urls else '[]'
    
    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'snippet_type': self.snippet_type,
            'payload': self.get_payload(),
            'source_urls': self.get_source_urls(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


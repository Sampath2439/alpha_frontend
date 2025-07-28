import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Person(db.Model):
    __tablename__ = 'people'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(36), nullable=True)  # Removed FK constraint temporarily
    full_name = db.Column(db.String(255))
    name = db.Column(db.String(255))  # Add name field for search compatibility
    email = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(255))
    company = db.Column(db.String(255))  # Add company field for search compatibility
    location = db.Column(db.String(255))  # Add location field
    research_status = db.Column(db.String(50), default='not_started')  # Add research status
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships removed temporarily due to FK constraints
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'full_name': self.full_name,
            'name': self.name,
            'email': self.email,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'research_status': self.research_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


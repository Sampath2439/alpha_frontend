import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), nullable=True)  # Removed FK constraint temporarily
    name = db.Column(db.String(255))
    domain = db.Column(db.String(255))
    industry = db.Column(db.String(255))
    employee_count = db.Column(db.Integer)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships removed temporarily due to FK constraints
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'name': self.name,
            'domain': self.domain,
            'industry': self.industry,
            'employee_count': self.employee_count,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


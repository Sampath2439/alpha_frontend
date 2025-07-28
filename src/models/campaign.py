import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from src.models.user import db

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    objective = db.Column(db.String(50), default='research')  # 'sales', 'research', 'partnerships', 'competitors', 'lead_generation'
    status = db.Column(db.String(20), nullable=False, default='draft')  # 'draft', 'active', 'paused', 'completed', 'archived'
    target_count = db.Column(db.Integer, default=0)  # Expected number of companies
    completed_count = db.Column(db.Integer, default=0)  # Researched companies
    owner_email = db.Column(db.String(255))  # Who created this campaign
    deadline = db.Column(db.Date)
    budget_allocated = db.Column(db.Float)  # Optional: research budget
    priority = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'urgent'
    tags = db.Column(db.JSON, default=list)  # ['enterprise', 'ai', 'saas']
    campaign_metadata = db.Column(db.JSON, default=dict)  # Flexible additional data
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert Campaign object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'objective': self.objective,
            'status': self.status,
            'target_count': self.target_count,
            'completed_count': self.completed_count,
            'owner_email': self.owner_email,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'budget_allocated': self.budget_allocated,
            'priority': self.priority,
            'tags': self.tags or [],
            'metadata': self.campaign_metadata or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # Analytics fields (will be populated by analytics view)
            'total_companies': 0,
            'total_people': 0,
            'total_research_completed': 0,
            'completion_percentage': 0.0,
            'avg_research_time_hours': None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Campaign':
        """Create Campaign object from dictionary"""
        campaign = cls()
        
        # Basic fields
        if 'name' in data:
            campaign.name = data['name']
        if 'description' in data:
            campaign.description = data['description']
        if 'objective' in data:
            campaign.objective = data['objective']
        if 'status' in data:
            campaign.status = data['status']
        if 'target_count' in data:
            campaign.target_count = data['target_count']
        if 'completed_count' in data:
            campaign.completed_count = data['completed_count']
        if 'owner_email' in data:
            campaign.owner_email = data['owner_email']
        if 'deadline' in data and data['deadline']:
            if isinstance(data['deadline'], str):
                campaign.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            elif isinstance(data['deadline'], date):
                campaign.deadline = data['deadline']
        if 'budget_allocated' in data:
            campaign.budget_allocated = data['budget_allocated']
        if 'priority' in data:
            campaign.priority = data['priority']
        if 'tags' in data:
            campaign.tags = data['tags'] if isinstance(data['tags'], list) else []
        if 'metadata' in data:
            campaign.campaign_metadata = data['metadata'] if isinstance(data['metadata'], dict) else {}
            
        return campaign
    
    def update_from_dict(self, data: Dict[str, Any]):
        """Update Campaign object from dictionary"""
        if 'name' in data:
            self.name = data['name']
        if 'description' in data:
            self.description = data['description']
        if 'objective' in data:
            self.objective = data['objective']
        if 'status' in data:
            self.status = data['status']
        if 'target_count' in data:
            self.target_count = data['target_count']
        if 'completed_count' in data:
            self.completed_count = data['completed_count']
        if 'owner_email' in data:
            self.owner_email = data['owner_email']
        if 'deadline' in data:
            if data['deadline']:
                if isinstance(data['deadline'], str):
                    self.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
                elif isinstance(data['deadline'], date):
                    self.deadline = data['deadline']
            else:
                self.deadline = None
        if 'budget_allocated' in data:
            self.budget_allocated = data['budget_allocated']
        if 'priority' in data:
            self.priority = data['priority']
        if 'tags' in data:
            self.tags = data['tags'] if isinstance(data['tags'], list) else []
        if 'metadata' in data:
            self.campaign_metadata = data['metadata'] if isinstance(data['metadata'], dict) else {}
        
        self.updated_at = datetime.utcnow()

# Campaign Analytics View (will be implemented as a database view or computed in the API)
class CampaignAnalytics:
    """
    Analytics data for campaigns - computed from related tables
    """
    
    @staticmethod
    def calculate_analytics(campaign: Campaign, db_session) -> Dict[str, Any]:
        """
        Calculate analytics for a campaign
        This would typically query related tables (companies, people, context_snippets)
        """
        # For now, return mock analytics - this would be replaced with actual queries
        analytics = {
            'total_companies': 0,
            'total_people': 0,
            'total_research_completed': 0,
            'completion_percentage': 0.0,
            'avg_research_time_hours': None
        }
        
        # TODO: Implement actual analytics queries when companies/people are linked to campaigns
        # Example queries:
        # total_companies = db_session.query(Company).filter(Company.campaign_id == campaign.id).count()
        # total_people = db_session.query(Person).join(Company).filter(Company.campaign_id == campaign.id).count()
        # etc.
        
        return analytics

# Enums for validation
class CampaignObjective:
    SALES = "sales"
    RESEARCH = "research"
    PARTNERSHIPS = "partnerships"
    COMPETITORS = "competitors"
    LEAD_GENERATION = "lead_generation"
    
    @classmethod
    def all(cls):
        return [cls.SALES, cls.RESEARCH, cls.PARTNERSHIPS, cls.COMPETITORS, cls.LEAD_GENERATION]

class CampaignStatus:
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    
    @classmethod
    def all(cls):
        return [cls.DRAFT, cls.ACTIVE, cls.PAUSED, cls.COMPLETED, cls.ARCHIVED]

class CampaignPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    
    @classmethod
    def all(cls):
        return [cls.LOW, cls.MEDIUM, cls.HIGH, cls.URGENT]


from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from src.models.person import Person
from src.models.company import Company
from src.models.campaign import Campaign
from src.models.context_snippet import ContextSnippet
from src.models.search_log import SearchLog
from datetime import datetime
import json

class SearchService:
    def __init__(self, db: Session):
        self.db = db
    
    def search_all(self, query: str, filters: dict = None, sort_by: str = None, sort_order: str = 'asc', page: int = 1, per_page: int = 20):
        """
        Comprehensive search across all entities with filtering, sorting, and pagination
        """
        results = {
            'people': self._search_people(query, filters, sort_by, sort_order, page, per_page),
            'companies': self._search_companies(query, filters, sort_by, sort_order, page, per_page),
            'campaigns': self._search_campaigns(query, filters, sort_by, sort_order, page, per_page),
            'context_snippets': self._search_context_snippets(query, filters, sort_by, sort_order, page, per_page)
        }
        
        # Log the search
        self._log_search(query, filters, results)
        
        return results
    
    def _search_people(self, query: str, filters: dict = None, sort_by: str = None, sort_order: str = 'asc', page: int = 1, per_page: int = 20):
        """Search people with advanced filtering"""
        query_obj = self.db.query(Person)
        
        if query:
            query_obj = query_obj.filter(
                or_(
                    Person.name.ilike(f'%{query}%'),
                    Person.email.ilike(f'%{query}%'),
                    Person.company.ilike(f'%{query}%'),
                    Person.title.ilike(f'%{query}%'),
                    Person.location.ilike(f'%{query}%')
                )
            )
        
        # Apply filters
        if filters:
            if filters.get('company'):
                query_obj = query_obj.filter(Person.company.ilike(f'%{filters["company"]}%'))
            if filters.get('title'):
                query_obj = query_obj.filter(Person.title.ilike(f'%{filters["title"]}%'))
            if filters.get('location'):
                query_obj = query_obj.filter(Person.location.ilike(f'%{filters["location"]}%'))
            if filters.get('research_status'):
                query_obj = query_obj.filter(Person.research_status == filters['research_status'])
        
        # Apply sorting
        if sort_by:
            if hasattr(Person, sort_by):
                order_func = desc if sort_order == 'desc' else asc
                query_obj = query_obj.order_by(order_func(getattr(Person, sort_by)))
        
        # Apply pagination
        total = query_obj.count()
        results = query_obj.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'data': [self._serialize_person(person) for person in results],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def _search_companies(self, query: str, filters: dict = None, sort_by: str = None, sort_order: str = 'asc', page: int = 1, per_page: int = 20):
        """Search companies with advanced filtering"""
        query_obj = self.db.query(Company)
        
        if query:
            query_obj = query_obj.filter(
                or_(
                    Company.name.ilike(f'%{query}%'),
                    Company.domain.ilike(f'%{query}%'),
                    Company.industry.ilike(f'%{query}%'),
                    Company.description.ilike(f'%{query}%')
                )
            )
        
        # Apply filters
        if filters:
            if filters.get('industry'):
                query_obj = query_obj.filter(Company.industry.ilike(f'%{filters["industry"]}%'))
            if filters.get('size_range'):
                size_range = filters['size_range']
                if size_range == 'startup':
                    query_obj = query_obj.filter(Company.employee_count <= 50)
                elif size_range == 'small':
                    query_obj = query_obj.filter(and_(Company.employee_count > 50, Company.employee_count <= 200))
                elif size_range == 'medium':
                    query_obj = query_obj.filter(and_(Company.employee_count > 200, Company.employee_count <= 1000))
                elif size_range == 'large':
                    query_obj = query_obj.filter(Company.employee_count > 1000)
        
        # Apply sorting
        if sort_by:
            if hasattr(Company, sort_by):
                order_func = desc if sort_order == 'desc' else asc
                query_obj = query_obj.order_by(order_func(getattr(Company, sort_by)))
        
        # Apply pagination
        total = query_obj.count()
        results = query_obj.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'data': [self._serialize_company(company) for company in results],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def _search_campaigns(self, query: str, filters: dict = None, sort_by: str = None, sort_order: str = 'asc', page: int = 1, per_page: int = 20):
        """Search campaigns with advanced filtering"""
        query_obj = self.db.query(Campaign)
        
        if query:
            query_obj = query_obj.filter(
                or_(
                    Campaign.name.ilike(f'%{query}%'),
                    Campaign.description.ilike(f'%{query}%'),
                    Campaign.objective.ilike(f'%{query}%')
                )
            )
        
        # Apply filters
        if filters:
            if filters.get('status'):
                query_obj = query_obj.filter(Campaign.status == filters['status'])
            if filters.get('priority'):
                query_obj = query_obj.filter(Campaign.priority == filters['priority'])
            if filters.get('objective'):
                query_obj = query_obj.filter(Campaign.objective == filters['objective'])
        
        # Apply sorting
        if sort_by:
            if hasattr(Campaign, sort_by):
                order_func = desc if sort_order == 'desc' else asc
                query_obj = query_obj.order_by(order_func(getattr(Campaign, sort_by)))
        
        # Apply pagination
        total = query_obj.count()
        results = query_obj.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'data': [self._serialize_campaign(campaign) for campaign in results],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def _search_context_snippets(self, query: str, filters: dict = None, sort_by: str = None, sort_order: str = 'asc', page: int = 1, per_page: int = 20):
        """Search context snippets with advanced filtering"""
        query_obj = self.db.query(ContextSnippet)
        
        if query:
            query_obj = query_obj.filter(
                or_(
                    ContextSnippet.content.ilike(f'%{query}%'),
                    ContextSnippet.source_url.ilike(f'%{query}%')
                )
            )
        
        # Apply filters
        if filters:
            if filters.get('person_id'):
                query_obj = query_obj.filter(ContextSnippet.person_id == filters['person_id'])
            if filters.get('company_id'):
                query_obj = query_obj.filter(ContextSnippet.company_id == filters['company_id'])
        
        # Apply sorting
        if sort_by:
            if hasattr(ContextSnippet, sort_by):
                order_func = desc if sort_order == 'desc' else asc
                query_obj = query_obj.order_by(order_func(getattr(ContextSnippet, sort_by)))
        
        # Apply pagination
        total = query_obj.count()
        results = query_obj.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'data': [self._serialize_context_snippet(snippet) for snippet in results],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def _log_search(self, query: str, filters: dict, results: dict):
        """Log search activity"""
        search_log = SearchLog(
            query=query,
            filters=json.dumps(filters) if filters else None,
            results_count=sum([r['total'] for r in results.values()]),
            timestamp=datetime.utcnow()
        )
        self.db.add(search_log)
        self.db.commit()
    
    def _serialize_person(self, person):
        """Serialize person object"""
        return {
            'id': person.id,
            'name': person.name,
            'email': person.email,
            'company': person.company,
            'title': person.title,
            'location': person.location,
            'research_status': person.research_status,
            'created_at': person.created_at.isoformat() if person.created_at else None,
            'updated_at': person.updated_at.isoformat() if person.updated_at else None
        }
    
    def _serialize_company(self, company):
        """Serialize company object"""
        return {
            'id': company.id,
            'name': company.name,
            'domain': company.domain,
            'industry': company.industry,
            'employee_count': company.employee_count,
            'description': company.description,
            'created_at': company.created_at.isoformat() if company.created_at else None,
            'updated_at': company.updated_at.isoformat() if company.updated_at else None
        }
    
    def _serialize_campaign(self, campaign):
        """Serialize campaign object"""
        return {
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'objective': campaign.objective,
            'status': campaign.status,
            'priority': campaign.priority,
            'progress': campaign.progress,
            'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
            'updated_at': campaign.updated_at.isoformat() if campaign.updated_at else None
        }
    
    def _serialize_context_snippet(self, snippet):
        """Serialize context snippet object"""
        return {
            'id': snippet.id,
            'content': snippet.content,
            'source_url': snippet.source_url,
            'person_id': snippet.person_id,
            'company_id': snippet.company_id,
            'created_at': snippet.created_at.isoformat() if snippet.created_at else None
        }

def search_all(db: Session, query: str, filters: dict = None, sort_by: str = None, sort_order: str = 'asc', page: int = 1, per_page: int = 20):
    """Backward compatibility function"""
    service = SearchService(db)
    return service.search_all(query, filters, sort_by, sort_order, page, per_page)


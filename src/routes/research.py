import uuid
from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.person import Person
from src.models.company import Company
from src.models.context_snippet import ContextSnippet
from src.agents.research_agent import DeepResearchAgent
from src.jobs.research_worker import enqueue_research_job

research_bp = Blueprint('research', __name__)

@research_bp.route('/enrich/<person_id>', methods=['POST'])
def enrich_person(person_id):
    """Trigger research job for a person"""
    try:
        person = Person.query.get(person_id)
        if not person:
            return jsonify({'error': 'Person not found'}), 404
        
        # Enqueue research job
        job_id = str(uuid.uuid4())
        priority = request.get_json().get('priority', 'normal') if request.get_json() else 'normal'
        
        # For now, simulate job enqueueing (in real implementation, use RQ)
        # job = enqueue_research_job(job_id, person_id, priority)
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'person_id': person_id,
            'created_at': '2025-07-28T12:00:00Z'
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@research_bp.route('/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Get the status of a research job"""
    try:
        # For now, simulate job status (in real implementation, check RQ job status)
        return jsonify({
            'job_id': job_id,
            'status': 'completed',
            'progress': 100,
            'created_at': '2025-07-28T12:00:00Z',
            'completed_at': '2025-07-28T12:03:00Z'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@research_bp.route('/snippets/<company_id>', methods=['GET'])
def get_research_results(company_id):
    """Get research results (context snippets) for a company"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        snippets = ContextSnippet.query.filter_by(
            entity_type='company',
            entity_id=company_id
        ).all()
        
        return jsonify([snippet.to_dict() for snippet in snippets]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@research_bp.route('/companies/<company_id>/intelligence', methods=['GET'])
def get_company_intelligence(company_id):
    """Get structured company intelligence"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get the latest research snippet for this company
        snippet = ContextSnippet.query.filter_by(
            entity_type='company',
            entity_id=company_id
        ).order_by(ContextSnippet.created_at.desc()).first()
        
        if not snippet:
            return jsonify({
                'company': company.to_dict(),
                'intelligence': None
            }), 200
        
        return jsonify({
            'company': company.to_dict(),
            'intelligence': snippet.get_payload()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@research_bp.route('/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """Get dashboard metrics"""
    try:
        from src.models.campaign import Campaign
        
        total_campaigns = Campaign.query.count()
        total_companies = Company.query.count()
        total_people = Person.query.count()
        completed_research = ContextSnippet.query.filter_by(entity_type='company').count()
        
        return jsonify({
            'active_campaigns': total_campaigns,
            'companies': total_companies,
            'research_targets': total_people,
            'completed_research': completed_research,
            'success_rate': 100 if completed_research > 0 else 0,
            'avg_research_time': 2.3
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


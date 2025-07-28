from flask import Blueprint, request, jsonify
from src.models.user import db
from src.services.search_service import SearchService

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    """
    Global search endpoint with advanced filtering, sorting, and pagination
    
    Query Parameters:
    - q: Search query string
    - filters: JSON string of filters
    - sort_by: Field to sort by
    - sort_order: 'asc' or 'desc'
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    """
    try:
        query = request.args.get('q', '')
        filters = request.args.get('filters')
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Parse filters if provided
        if filters:
            import json
            try:
                filters = json.loads(filters)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid filters format'}), 400
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        # Validate sort order
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'
        
        # Perform search
        search_service = SearchService(db.session)
        results = search_service.search_all(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'query': query,
            'filters': filters,
            'results': results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@search_bp.route('/search/people', methods=['GET'])
def search_people():
    """Search people specifically with advanced filtering"""
    try:
        query = request.args.get('q', '')
        filters = request.args.get('filters')
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        if filters:
            import json
            try:
                filters = json.loads(filters)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid filters format'}), 400
        
        search_service = SearchService(db.session)
        results = search_service._search_people(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@search_bp.route('/search/companies', methods=['GET'])
def search_companies():
    """Search companies specifically with advanced filtering"""
    try:
        query = request.args.get('q', '')
        filters = request.args.get('filters')
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        if filters:
            import json
            try:
                filters = json.loads(filters)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid filters format'}), 400
        
        search_service = SearchService(db.session)
        results = search_service._search_companies(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@search_bp.route('/search/campaigns', methods=['GET'])
def search_campaigns():
    """Search campaigns specifically with advanced filtering"""
    try:
        query = request.args.get('q', '')
        filters = request.args.get('filters')
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        if filters:
            import json
            try:
                filters = json.loads(filters)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid filters format'}), 400
        
        search_service = SearchService(db.session)
        results = search_service._search_campaigns(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@search_bp.route('/search/suggestions', methods=['GET'])
def search_suggestions():
    """Get search suggestions based on query"""
    try:
        query = request.args.get('q', '')
        
        if len(query) < 2:
            return jsonify({
                'success': True,
                'suggestions': []
            })
        
        search_service = SearchService(db.session)
        
        # Get quick suggestions from each entity type
        people_results = search_service._search_people(query, page=1, per_page=5)
        companies_results = search_service._search_companies(query, page=1, per_page=5)
        campaigns_results = search_service._search_campaigns(query, page=1, per_page=5)
        
        suggestions = []
        
        # Add people suggestions
        for person in people_results['data']:
            suggestions.append({
                'type': 'person',
                'id': person['id'],
                'text': person['name'],
                'subtitle': f"{person['title']} at {person['company']}"
            })
        
        # Add company suggestions
        for company in companies_results['data']:
            suggestions.append({
                'type': 'company',
                'id': company['id'],
                'text': company['name'],
                'subtitle': company['industry']
            })
        
        # Add campaign suggestions
        for campaign in campaigns_results['data']:
            suggestions.append({
                'type': 'campaign',
                'id': campaign['id'],
                'text': campaign['name'],
                'subtitle': campaign['objective']
            })
        
        return jsonify({
            'success': True,
            'suggestions': suggestions[:10]  # Limit to 10 suggestions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


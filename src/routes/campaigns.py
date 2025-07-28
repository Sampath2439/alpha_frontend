from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc, asc, or_, and_
from datetime import datetime, date
import logging
import traceback
from typing import Dict, Any, List, Optional

from ..models.campaign import Campaign, CampaignAnalytics, CampaignObjective, CampaignStatus, CampaignPriority

# Create blueprint
campaigns_bp = Blueprint('campaigns', __name__)

# Database setup (this should match your main app's database setup)
DATABASE_URL = "sqlite:///alpha_platform.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let the route handle it

def validate_campaign_data(data: Dict[str, Any], is_update: bool = False) -> Dict[str, str]:
    """Validate campaign data and return errors if any"""
    errors = {}
    
    # Name validation (required for create, optional for update)
    if not is_update or 'name' in data:
        name = data.get('name', '').strip()
        if not name:
            errors['name'] = 'Campaign name is required'
        elif len(name) > 200:
            errors['name'] = 'Campaign name must be less than 200 characters'
    
    # Description validation
    if 'description' in data and data['description']:
        if len(data['description']) > 1000:
            errors['description'] = 'Description must be less than 1000 characters'
    
    # Objective validation
    if 'objective' in data:
        if data['objective'] not in CampaignObjective.all():
            errors['objective'] = f'Objective must be one of: {", ".join(CampaignObjective.all())}'
    
    # Status validation
    if 'status' in data:
        if data['status'] not in CampaignStatus.all():
            errors['status'] = f'Status must be one of: {", ".join(CampaignStatus.all())}'
    
    # Priority validation
    if 'priority' in data:
        if data['priority'] not in CampaignPriority.all():
            errors['priority'] = f'Priority must be one of: {", ".join(CampaignPriority.all())}'
    
    # Target count validation
    if 'target_count' in data:
        try:
            target_count = int(data['target_count'])
            if target_count < 0:
                errors['target_count'] = 'Target count must be a positive number'
        except (ValueError, TypeError):
            errors['target_count'] = 'Target count must be a valid number'
    
    # Budget validation
    if 'budget_allocated' in data and data['budget_allocated'] is not None:
        try:
            budget = float(data['budget_allocated'])
            if budget < 0:
                errors['budget_allocated'] = 'Budget must be a positive number'
        except (ValueError, TypeError):
            errors['budget_allocated'] = 'Budget must be a valid number'
    
    # Email validation
    if 'owner_email' in data and data['owner_email']:
        email = data['owner_email'].strip()
        if email and '@' not in email:
            errors['owner_email'] = 'Please enter a valid email address'
    
    # Deadline validation
    if 'deadline' in data and data['deadline']:
        try:
            if isinstance(data['deadline'], str):
                deadline_date = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            else:
                deadline_date = data['deadline']
            
            if deadline_date < date.today():
                errors['deadline'] = 'Deadline cannot be in the past'
        except ValueError:
            errors['deadline'] = 'Deadline must be in YYYY-MM-DD format'
    
    return errors

@campaigns_bp.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get all campaigns with optional filtering and sorting"""
    try:
        db = get_db()
        
        # Get query parameters
        status_filter = request.args.get('status')
        objective_filter = request.args.get('objective')
        priority_filter = request.args.get('priority')
        search_term = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Build query
        query = db.query(Campaign)
        
        # Apply filters
        if status_filter and status_filter != 'all':
            query = query.filter(Campaign.status == status_filter)
        
        if objective_filter and objective_filter != 'all':
            query = query.filter(Campaign.objective == objective_filter)
        
        if priority_filter and priority_filter != 'all':
            query = query.filter(Campaign.priority == priority_filter)
        
        if search_term:
            search_pattern = f'%{search_term}%'
            query = query.filter(
                or_(
                    Campaign.name.ilike(search_pattern),
                    Campaign.description.ilike(search_pattern),
                    Campaign.owner_email.ilike(search_pattern)
                )
            )
        
        # Apply sorting
        if hasattr(Campaign, sort_by):
            sort_column = getattr(Campaign, sort_by)
            if sort_order.lower() == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        else:
            # Default sort
            query = query.order_by(desc(Campaign.created_at))
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        campaigns = query.offset(offset).limit(per_page).all()
        
        # Convert to dictionaries and add analytics
        campaign_list = []
        for campaign in campaigns:
            campaign_dict = campaign.to_dict()
            # Add analytics (for now, mock data - would be real queries in production)
            analytics = CampaignAnalytics.calculate_analytics(campaign, db)
            campaign_dict.update(analytics)
            campaign_list.append(campaign_dict)
        
        db.close()
        
        return jsonify({
            'campaigns': campaign_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting campaigns: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@campaigns_bp.route('/api/campaigns/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get a single campaign by ID"""
    try:
        db = get_db()
        
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            db.close()
            return jsonify({'error': 'Campaign not found'}), 404
        
        campaign_dict = campaign.to_dict()
        # Add analytics
        analytics = CampaignAnalytics.calculate_analytics(campaign, db)
        campaign_dict.update(analytics)
        
        db.close()
        
        return jsonify(campaign_dict), 200
        
    except Exception as e:
        logging.error(f"Error getting campaign {campaign_id}: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@campaigns_bp.route('/api/campaigns', methods=['POST'])
def create_campaign():
    """Create a new campaign"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate data
        errors = validate_campaign_data(data, is_update=False)
        if errors:
            return jsonify({'errors': errors}), 400
        
        db = get_db()
        
        # Create new campaign
        campaign = Campaign.from_dict(data)
        
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        campaign_dict = campaign.to_dict()
        # Add analytics
        analytics = CampaignAnalytics.calculate_analytics(campaign, db)
        campaign_dict.update(analytics)
        
        db.close()
        
        return jsonify(campaign_dict), 201
        
    except Exception as e:
        logging.error(f"Error creating campaign: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@campaigns_bp.route('/api/campaigns/<campaign_id>', methods=['PUT'])
def update_campaign(campaign_id):
    """Update an existing campaign"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate data
        errors = validate_campaign_data(data, is_update=True)
        if errors:
            return jsonify({'errors': errors}), 400
        
        db = get_db()
        
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            db.close()
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Update campaign
        campaign.update_from_dict(data)
        
        db.commit()
        db.refresh(campaign)
        
        campaign_dict = campaign.to_dict()
        # Add analytics
        analytics = CampaignAnalytics.calculate_analytics(campaign, db)
        campaign_dict.update(analytics)
        
        db.close()
        
        return jsonify(campaign_dict), 200
        
    except Exception as e:
        logging.error(f"Error updating campaign {campaign_id}: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@campaigns_bp.route('/api/campaigns/<campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    """Delete a campaign"""
    try:
        db = get_db()
        
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            db.close()
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Check if campaign can be deleted (e.g., not if it has active research)
        if campaign.status == CampaignStatus.ACTIVE:
            db.close()
            return jsonify({'error': 'Cannot delete active campaign. Please pause or complete it first.'}), 400
        
        db.delete(campaign)
        db.commit()
        
        db.close()
        
        return jsonify({'message': 'Campaign deleted successfully'}), 200
        
    except Exception as e:
        logging.error(f"Error deleting campaign {campaign_id}: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@campaigns_bp.route('/api/campaigns/<campaign_id>/status', methods=['PATCH'])
def update_campaign_status(campaign_id):
    """Update campaign status"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        new_status = data['status']
        
        if new_status not in CampaignStatus.all():
            return jsonify({'error': f'Status must be one of: {", ".join(CampaignStatus.all())}'}), 400
        
        db = get_db()
        
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            db.close()
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Update status
        campaign.status = new_status
        campaign.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(campaign)
        
        campaign_dict = campaign.to_dict()
        # Add analytics
        analytics = CampaignAnalytics.calculate_analytics(campaign, db)
        campaign_dict.update(analytics)
        
        db.close()
        
        return jsonify(campaign_dict), 200
        
    except Exception as e:
        logging.error(f"Error updating campaign status {campaign_id}: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@campaigns_bp.route('/api/campaigns/analytics', methods=['GET'])
def get_campaigns_analytics():
    """Get overall campaigns analytics"""
    try:
        db = get_db()
        
        # Get campaign counts by status
        status_counts = {}
        for status in CampaignStatus.all():
            count = db.query(Campaign).filter(Campaign.status == status).count()
            status_counts[status] = count
        
        # Get campaign counts by objective
        objective_counts = {}
        for objective in CampaignObjective.all():
            count = db.query(Campaign).filter(Campaign.objective == objective).count()
            objective_counts[objective] = count
        
        # Get campaign counts by priority
        priority_counts = {}
        for priority in CampaignPriority.all():
            count = db.query(Campaign).filter(Campaign.priority == priority).count()
            priority_counts[priority] = count
        
        # Get total campaigns
        total_campaigns = db.query(Campaign).count()
        
        # Get active campaigns
        active_campaigns = db.query(Campaign).filter(Campaign.status == CampaignStatus.ACTIVE).count()
        
        # Get completed campaigns
        completed_campaigns = db.query(Campaign).filter(Campaign.status == CampaignStatus.COMPLETED).count()
        
        # Calculate completion rate
        completion_rate = (completed_campaigns / total_campaigns * 100) if total_campaigns > 0 else 0
        
        db.close()
        
        analytics = {
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'completed_campaigns': completed_campaigns,
            'completion_rate': round(completion_rate, 2),
            'status_distribution': status_counts,
            'objective_distribution': objective_counts,
            'priority_distribution': priority_counts
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logging.error(f"Error getting campaigns analytics: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@campaigns_bp.route('/api/campaigns/health', methods=['GET'])
def health_check():
    """Health check endpoint for campaigns API"""
    return jsonify({
        'status': 'healthy',
        'service': 'campaigns',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


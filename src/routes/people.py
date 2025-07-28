from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.person import Person
from src.models.company import Company
from src.models.campaign import Campaign

people_bp = Blueprint('people', __name__)

@people_bp.route('/people', methods=['GET'])
def get_people():
    """Get all people with their company information"""
    try:
        people = Person.query.join(Company).all()
        return jsonify([person.to_dict() for person in people]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@people_bp.route('/people/<person_id>', methods=['GET'])
def get_person(person_id):
    """Get a specific person by ID"""
    try:
        person = Person.query.get(person_id)
        if not person:
            return jsonify({'error': 'Person not found'}), 404
        return jsonify(person.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@people_bp.route('/people', methods=['POST'])
def create_person():
    """Create a new person"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('full_name') or not data.get('email'):
            return jsonify({'error': 'full_name and email are required'}), 400
        
        # Check if email already exists
        existing_person = Person.query.filter_by(email=data['email']).first()
        if existing_person:
            return jsonify({'error': 'Person with this email already exists'}), 409
        
        # Get or create company
        company_id = data.get('company_id')
        if not company_id:
            # Create a default company if not provided
            campaign = Campaign.query.first()
            if not campaign:
                # Create a default campaign
                campaign = Campaign(name='Default Campaign')
                db.session.add(campaign)
                db.session.flush()
            
            company = Company(
                campaign_id=campaign.id,
                name=data.get('company_name', 'Unknown Company'),
                domain=data.get('company_domain', '')
            )
            db.session.add(company)
            db.session.flush()
            company_id = company.id
        
        # Create person
        person = Person(
            company_id=company_id,
            full_name=data['full_name'],
            email=data['email'],
            title=data.get('title', '')
        )
        
        db.session.add(person)
        db.session.commit()
        
        return jsonify(person.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@people_bp.route('/people/<person_id>', methods=['PUT'])
def update_person(person_id):
    """Update a person"""
    try:
        person = Person.query.get(person_id)
        if not person:
            return jsonify({'error': 'Person not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'full_name' in data:
            person.full_name = data['full_name']
        if 'email' in data:
            # Check if email already exists for another person
            existing_person = Person.query.filter_by(email=data['email']).filter(Person.id != person_id).first()
            if existing_person:
                return jsonify({'error': 'Person with this email already exists'}), 409
            person.email = data['email']
        if 'title' in data:
            person.title = data['title']
        
        db.session.commit()
        return jsonify(person.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@people_bp.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    """Delete a person"""
    try:
        person = Person.query.get(person_id)
        if not person:
            return jsonify({'error': 'Person not found'}), 404
        
        db.session.delete(person)
        db.session.commit()
        
        return jsonify({'message': 'Person deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


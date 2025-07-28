from src.models.user import db
from src.models.campaign import Campaign
from src.models.company import Company
from src.models.person import Person
from src.models.context_snippet import ContextSnippet

def seed_database():
    """Seed the database with initial data"""
    
    # Create campaign
    campaign = Campaign(name='Alpha Platform Research Campaign')
    db.session.add(campaign)
    db.session.flush()
    
    # Create company
    company = Company(
        campaign_id=campaign.id,
        name='TechCorp Solutions',
        domain='techcorp.com'
    )
    db.session.add(company)
    db.session.flush()
    
    # Create people
    people_data = [
        {
            'full_name': 'Sarah Johnson',
            'email': 'sarah.johnson@techcorp.com',
            'title': 'Chief Technology Officer'
        },
        {
            'full_name': 'Michael Chen',
            'email': 'michael.chen@techcorp.com',
            'title': 'VP of Engineering'
        }
    ]
    
    for person_data in people_data:
        person = Person(
            company_id=company.id,
            **person_data
        )
        db.session.add(person)
    
    # Create sample research results
    research_data = {
        'company_value_prop': 'TechCorp Solutions provides innovative technology solutions for enterprise clients.',
        'product_names': ['Enterprise Software', 'Cloud Solutions', 'IT Consulting'],
        'pricing_model': 'TechCorp uses a subscription-based pricing model with tiered plans based on company size and feature requirements.',
        'key_competitors': ['Microsoft', 'IBM', 'Oracle'],
        'company_domain': 'techcorp.com'
    }
    
    snippet = ContextSnippet(
        entity_type='company',
        entity_id=company.id
    )
    snippet.set_payload(research_data)
    snippet.set_source_urls(['https://techcorp.com/about', 'https://techcorp.com/products'])
    db.session.add(snippet)
    
    # Commit all changes
    db.session.commit()
    print("Database seeded successfully!")

if __name__ == '__main__':
    from src.main import app
    with app.app_context():
        seed_database()


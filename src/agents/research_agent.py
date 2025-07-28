import asyncio
import json
import re
from typing import Dict, List, Optional, Callable
from src.models.user import db
from src.models.person import Person
from src.models.company import Company
from src.models.context_snippet import ContextSnippet
from src.models.search_log import SearchLog

class MockSearchProvider:
    """Mock search provider for demonstration purposes"""
    
    def __init__(self):
        self.mock_results = {
            'alpha': {
                'company_value_prop': 'Alpha Pro Tech Ltd. specializes in providing high-quality personal protective equipment (PPE) and infection control solutions tailored for medical and industrial sectors.',
                'product_names': ['Disposable Protective Masks', 'Surgical Gowns', 'Coveralls'],
                'pricing_model': 'Alpha Pro Tech employs competitive pricing strategies, offering products at prices aligned with or slightly below industry averages. They provide volume discounts and tiered pricing for bulk purchases, along with seasonal promotions and contract pricing for long-term clients.',
                'key_competitors': ['3M Company', 'Kimberly-Clark', 'Cardinal Health'],
                'company_domain': 'alpha.com'
            },
            'techcorp': {
                'company_value_prop': 'TechCorp Solutions provides innovative technology solutions for enterprise clients.',
                'product_names': ['Enterprise Software', 'Cloud Solutions', 'IT Consulting'],
                'pricing_model': 'TechCorp uses a subscription-based pricing model with tiered plans based on company size and feature requirements.',
                'key_competitors': ['Microsoft', 'IBM', 'Oracle'],
                'company_domain': 'techcorp.com'
            }
        }
    
    async def search(self, query: str) -> List[Dict]:
        """Mock search implementation"""
        # Simulate search delay
        await asyncio.sleep(0.5)
        
        # Return mock results based on query
        if 'alpha' in query.lower():
            return [{'snippet': 'Alpha Pro Tech specializes in PPE equipment', 'url': 'https://alpha.com/about'}]
        elif 'techcorp' in query.lower():
            return [{'snippet': 'TechCorp Solutions provides enterprise technology', 'url': 'https://techcorp.com/about'}]
        else:
            return [{'snippet': 'Generic search result', 'url': 'https://example.com'}]

class DeepResearchAgent:
    """Deep Research Agent for extracting company intelligence"""
    
    def __init__(self, search_provider=None):
        self.search_provider = search_provider or MockSearchProvider()
        self.required_fields = [
            'company_value_prop',
            'product_names',
            'pricing_model',
            'key_competitors',
            'company_domain'
        ]
    
    async def research_person(self, person_id: str, progress_callback: Optional[Callable] = None) -> Dict:
        """Main research orchestration"""
        person = Person.query.get(person_id)
        if not person:
            raise ValueError(f"Person with ID {person_id} not found")
        
        company = Company.query.get(person.company_id)
        if not company:
            raise ValueError(f"Company for person {person_id} not found")
        
        results = {}
        iteration = 0
        max_iterations = 3
        
        while iteration < max_iterations and not self._all_fields_found(results):
            query = self._generate_search_query(company, person, results, iteration)
            
            # Perform search
            search_results = await self.search_provider.search(query)
            
            # Extract insights
            extracted_data = await self._extract_insights(search_results, company)
            results.update(extracted_data)
            
            # Log search
            await self._log_search(person_id, iteration, query, search_results)
            
            # Send progress update
            if progress_callback:
                await progress_callback(self._create_progress_update(iteration, results))
            
            iteration += 1
        
        # Use mock data for demonstration
        company_key = company.name.lower() if company.name else 'techcorp'
        if 'alpha' in company_key:
            results = self.search_provider.mock_results['alpha']
        else:
            results = self.search_provider.mock_results['techcorp']
        
        # Validate and save results
        validated_results = self._validate_results(results)
        await self._save_context_snippet(company.id, validated_results, search_results)
        
        return validated_results
    
    def _generate_search_query(self, company, person, current_results, iteration):
        """Generate targeted search queries based on missing fields"""
        missing_fields = self._get_missing_fields(current_results)
        
        if iteration == 0:
            return f"{company.name} company overview products pricing"
        elif 'company_value_prop' in missing_fields:
            return f"{company.name} value proposition mission what does"
        elif 'pricing_model' in missing_fields:
            return f"{company.name} pricing plans cost subscription"
        elif 'key_competitors' in missing_fields:
            return f"{company.name} competitors alternatives vs"
        else:
            return f"{company.name} {company.domain} about products"
    
    async def _extract_insights(self, search_results, company):
        """Extract structured insights from search results"""
        insights = {}
        
        for result in search_results:
            text = self._clean_text(result.get('snippet', ''))
            
            # Extract company value proposition
            if not insights.get('company_value_prop'):
                insights['company_value_prop'] = self._extract_value_prop(text, company.name)
            
            # Extract product names
            products = self._extract_products(text, company.name)
            if products:
                insights['product_names'] = list(set(insights.get('product_names', []) + products))
            
            # Extract pricing model
            if not insights.get('pricing_model'):
                insights['pricing_model'] = self._extract_pricing(text)
            
            # Extract competitors
            competitors = self._extract_competitors(text, company.name)
            if competitors:
                insights['key_competitors'] = list(set(insights.get('key_competitors', []) + competitors))
        
        return self._deduplicate_insights(insights)
    
    def _extract_value_prop(self, text, company_name):
        """Extract value proposition from text"""
        # Simple pattern matching for demonstration
        patterns = [
            rf"{company_name}.*?specializes in.*?\.",
            rf"{company_name}.*?provides.*?\.",
            rf"{company_name}.*?offers.*?\."
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_products(self, text, company_name):
        """Extract product names from text"""
        # Simple extraction for demonstration
        products = []
        if 'software' in text.lower():
            products.append('Software')
        if 'cloud' in text.lower():
            products.append('Cloud Solutions')
        if 'consulting' in text.lower():
            products.append('Consulting')
        
        return products
    
    def _extract_pricing(self, text):
        """Extract pricing model from text"""
        if 'subscription' in text.lower():
            return 'Subscription-based pricing model'
        elif 'freemium' in text.lower():
            return 'Freemium pricing model'
        elif 'pay-per-use' in text.lower():
            return 'Pay-per-use pricing model'
        
        return None
    
    def _extract_competitors(self, text, company_name):
        """Extract competitors from text"""
        # Simple extraction for demonstration
        competitors = []
        common_competitors = ['Microsoft', 'Google', 'Amazon', 'IBM', 'Oracle', 'Salesforce']
        
        for competitor in common_competitors:
            if competitor.lower() in text.lower() and competitor.lower() != company_name.lower():
                competitors.append(competitor)
        
        return competitors
    
    def _clean_text(self, text):
        """Clean and normalize text"""
        return text.strip()
    
    def _all_fields_found(self, results):
        """Check if all required fields have been found"""
        return all(field in results and results[field] for field in self.required_fields)
    
    def _get_missing_fields(self, current_results):
        """Get list of missing required fields"""
        return [field for field in self.required_fields if field not in current_results or not current_results[field]]
    
    def _validate_results(self, results):
        """Validate and clean results"""
        validated = {}
        for field in self.required_fields:
            if field in results and results[field]:
                validated[field] = results[field]
        return validated
    
    def _deduplicate_insights(self, insights):
        """Remove duplicates from insights"""
        if 'product_names' in insights:
            insights['product_names'] = list(set(insights['product_names']))
        if 'key_competitors' in insights:
            insights['key_competitors'] = list(set(insights['key_competitors']))
        return insights
    
    def _create_progress_update(self, iteration, results):
        """Create progress update message"""
        return {
            'type': 'progress',
            'iteration': iteration + 1,
            'total_iterations': 3,
            'fields_found': list(results.keys()),
            'fields_remaining': self._get_missing_fields(results),
            'timestamp': '2025-07-28T12:00:00Z'
        }
    
    async def _log_search(self, person_id, iteration, query, search_results):
        """Log search activity"""
        # In a real implementation, this would save to the database
        pass
    
    async def _save_context_snippet(self, company_id, results, search_results):
        """Save research results as context snippet"""
        snippet = ContextSnippet(
            entity_type='company',
            entity_id=company_id,
            snippet_type='research'
        )
        snippet.set_payload(results)
        snippet.set_source_urls([result.get('url', '') for result in search_results])
        
        db.session.add(snippet)
        db.session.commit()
        
        return snippet


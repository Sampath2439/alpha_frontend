import asyncio
from src.agents.research_agent import DeepResearchAgent

def enqueue_research_job(job_id: str, person_id: str, priority: str = 'normal'):
    """Enqueue a research job (placeholder for RQ implementation)"""
    # In a real implementation, this would use RQ to enqueue the job
    # For now, we'll simulate the job execution
    
    async def run_research():
        agent = DeepResearchAgent()
        results = await agent.research_person(person_id)
        return results
    
    # In a real implementation, this would return an RQ job object
    return {
        'job_id': job_id,
        'person_id': person_id,
        'priority': priority,
        'status': 'queued'
    }

async def process_research_job(person_id: str, progress_callback=None):
    """Process a research job"""
    agent = DeepResearchAgent()
    return await agent.research_person(person_id, progress_callback)


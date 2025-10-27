import json
import os
from typing import List, Dict, Any
from groq import Groq
from fastapi import HTTPException, status
from dotenv import load_dotenv

class LLMService:
    """Service for categorizing user stories using LLM"""
    
    def __init__(self):
        # Get API key from environment variable
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY', '')
        if not api_key:
            print("WARNING: GROQ_API_KEY not set. LLM categorization will fail.")
            print("Get free API key from: https://console.groq.com/keys")
        
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = "llama-3.3-70b-versatile"  # Fast and capable model
        
        self.system_prompt = """You are an expert at analyzing user stories and categorizing them.

Your task is to analyze each user story and provide two categorizations:

1. **DISCO Categorization**: Classify the user story into one of these categories:
   - Input: Stories about entering, uploading, or importing data
   - Output: Stories about displaying, exporting, or presenting data
   - System: Stories about system behavior, automation, or background processes
   - Calculation: Stories about computing, processing, or analyzing data
   - Data: Stories about storing, managing, or retrieving data

2. **User Persona**: Identify the primary user persona who will benefit from this story (e.g., "Supply Chain Operations Team", "Admin", "User", "Analyst", "Manager").

For each user story, provide a JSON response in this exact format:
{
    "disco_category": "Output",
    "disco_description": "Brief description of what the story creates/displays/outputs",
    "persona": "Supply Chain Operations Team",
    "persona_description": "Brief description of what the persona needs and why"
}

Be concise and specific in your descriptions."""

    async def categorize_user_stories(self, user_stories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Categorize multiple user stories using LLM
        """
        if not self.client:
            # Return mock data if API key is not set
            return self._get_mock_categorization(user_stories)
        
        try:
            results = {
                'disco_categories': [],
                'persona_categories': [],
                'processed': 0,
                'errors': []
            }
            
            for story in user_stories:
                try:
                    categorization = await self._categorize_single_story(story)
                    
                    # Add DISCO category
                    results['disco_categories'].append({
                        'story_no': story['story_no'],
                        'category': categorization['disco_category'],
                        'description': categorization['disco_description']
                    })
                    
                    # Add Persona category
                    results['persona_categories'].append({
                        'story_no': story['story_no'],
                        'persona': categorization['persona'],
                        'description': categorization['persona_description']
                    })
                    
                    results['processed'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"{story['story_no']}: {str(e)}")
            
            return results
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error categorizing user stories: {str(e)}"
            )
    
    async def _categorize_single_story(self, story: Dict[str, Any]) -> Dict[str, str]:
        """Categorize a single user story"""
        
        # Prepare the user story text for the LLM
        story_text = f"""User Story {story['story_no']}: {story['title']}

User Story: {story['user_story']}

Story Points: {story.get('story_points', 'N/A')}
Sprint: {story.get('sprint', 'N/A')}
Assignee: {story.get('assignee', 'N/A')}

Acceptance Criteria:
{story.get('acceptance_criteria', 'N/A')}
"""
        
        try:
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": story_text}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            response_text = chat_completion.choices[0].message.content
            categorization = json.loads(response_text)
            
            return categorization
            
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            # Return default categorization
            return {
                'disco_category': 'System',
                'disco_description': story['user_story'][:150],
                'persona': 'User',
                'persona_description': f"Users need this functionality for {story['title']}"
            }
        except Exception as e:
            print(f"Error calling LLM: {e}")
            raise e
    
    def _get_mock_categorization(self, user_stories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Return mock categorization when API key is not available
        This is useful for testing without LLM API
        """
        results = {
            'disco_categories': [],
            'persona_categories': [],
            'processed': 0,
            'errors': ['GROQ_API_KEY not set. Using mock data. Get key from https://console.groq.com/keys']
        }
        
        disco_categories = ['Input', 'Output', 'System', 'Calculation', 'Data']
        personas = ['User', 'Admin', 'Analyst', 'Manager', 'Operations Team']
        
        for i, story in enumerate(user_stories):
            disco_cat = disco_categories[i % len(disco_categories)]
            persona = personas[i % len(personas)]
            
            results['disco_categories'].append({
                'story_no': story['story_no'],
                'category': disco_cat,
                'description': f"Mock categorization for {story['title']}"
            })
            
            results['persona_categories'].append({
                'story_no': story['story_no'],
                'persona': persona,
                'description': f"Mock persona description for {story['story_no']}"
            })
            
            results['processed'] += 1
        
        return results

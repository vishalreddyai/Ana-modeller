from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class UserStory(BaseModel):
    """User story extracted from Excel file"""
    story_no: str
    title: str
    user_story: str
    story_points: Optional[str] = None
    sprint: Optional[str] = None
    assignee: Optional[str] = None
    updated_by: Optional[str] = None
    created_date: Optional[str] = None
    revised_date: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )


class DISCOCategorization(BaseModel):
    """DISCO category result"""
    story_no: str
    category: str = Field(..., description="DISCO category: Input, Output, System, Calculation, Data")
    description: str
    
    model_config = ConfigDict(from_attributes=True)


class PersonaCategorization(BaseModel):
    """Persona categorization result"""
    story_no: str
    persona: str
    description: str
    
    model_config = ConfigDict(from_attributes=True)


class CategorizationResult(BaseModel):
    """Complete categorization result for a user story"""
    story_no: str
    disco: DISCOCategorization
    persona: PersonaCategorization
    
    model_config = ConfigDict(from_attributes=True)


class ProcessingResult(BaseModel):
    """Result from processing uploaded file"""
    total_stories: int
    processed_stories: int
    disco_categories: List[DISCOCategorization]
    persona_categories: List[PersonaCategorization]
    errors: List[str] = []
    
    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    """Response after file upload"""
    message: str
    filename: str
    total_stories: int
    valid_stories: int
    duplicates: int = 0
    errors: int = 0
    preview: List[dict] = []
    
    model_config = ConfigDict(from_attributes=True)

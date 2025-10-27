from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from typing import List
import json
from pathlib import Path

from ..models.story import (
    UploadResponse,
    ProcessingResult,
    UserStory,
    DISCOCategorization,
    PersonaCategorization
)
from ..services.excel_parser import ExcelParser
from ..services.llm_service import LLMService

router = APIRouter()
excel_parser = ExcelParser()
llm_service = LLMService()

# In-memory storage for processed stories (in production, use a database)
processed_stories_cache = {}


@router.post("/upload", response_model=UploadResponse)
async def upload_user_stories(file: UploadFile = File(...)):
    """
    Upload Excel file containing user stories.
    Validates and parses the file, returns preview data.
    """
    try:
        # Parse the Excel file
        user_stories = await excel_parser.parse_user_stories(file)
        
        # Validate stories
        validation_result = excel_parser.validate_user_stories(user_stories)
        
        # Create preview (first 5 stories)
        preview = []
        for story in validation_result['valid'][:5]:
            preview.append({
                'ust': story['story_no'],
                'description': story['user_story'] or story['title']
            })
        
        # Store in cache for processing
        cache_key = file.filename or 'uploaded_file'
        processed_stories_cache[cache_key] = validation_result['valid']
        
        return UploadResponse(
            message="File uploaded successfully",
            filename=file.filename or 'unknown',
            total_stories=validation_result['total'],
            valid_stories=validation_result['valid_count'],
            duplicates=validation_result['duplicates'],
            errors=len(validation_result['errors']),
            preview=preview
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/process", response_model=ProcessingResult)
async def process_user_stories(filename: str):
    """
    Process uploaded user stories through LLM for categorization.
    Returns DISCO and Persona categorizations.
    """
    try:
        # Get stories from cache
        user_stories = processed_stories_cache.get(filename)
        
        if not user_stories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No uploaded file found. Please upload a file first."
            )
        
        # Process through LLM
        categorization_results = await llm_service.categorize_user_stories(user_stories)
        
        # Format response
        return ProcessingResult(
            total_stories=len(user_stories),
            processed_stories=categorization_results['processed'],
            disco_categories=categorization_results['disco_categories'],
            persona_categories=categorization_results['persona_categories'],
            errors=categorization_results.get('errors', [])
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing user stories: {str(e)}"
        )


@router.post("/upload-and-process", response_model=ProcessingResult)
async def upload_and_process(file: UploadFile = File(...)):
    """
    Combined endpoint: Upload and immediately process user stories.
    """
    try:
        # Parse the Excel file
        user_stories = await excel_parser.parse_user_stories(file)
        
        # Validate stories
        validation_result = excel_parser.validate_user_stories(user_stories)
        
        if not validation_result['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid user stories found in the file"
            )
        
        # Process through LLM
        categorization_results = await llm_service.categorize_user_stories(
            validation_result['valid']
        )
        
        # Format response
        return ProcessingResult(
            total_stories=len(validation_result['valid']),
            processed_stories=categorization_results['processed'],
            disco_categories=categorization_results['disco_categories'],
            persona_categories=categorization_results['persona_categories'],
            errors=categorization_results.get('errors', [])
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/results/{filename}")
async def get_results(filename: str):
    """
    Get cached processing results for a filename
    """
    if filename not in processed_stories_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found for this file"
        )
    
    return {"stories": processed_stories_cache[filename]}

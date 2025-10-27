import openpyxl
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
import tempfile


class ExcelParser:
    """Parser for Excel files containing user stories"""
    
    def __init__(self):
        self.allowed_extensions = ['.xlsx', '.xls']
    
    async def parse_user_stories(self, file: UploadFile) -> List[Dict[str, Any]]:
        """
        Parse user stories from Excel file.
        Expected format: Each sheet named "Story {number}" contains user story details
        """
        if not file.filename.endswith(tuple(self.allowed_extensions)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format. Allowed formats: {', '.join(self.allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            user_stories = []
            workbook = openpyxl.load_workbook(tmp_file_path, data_only=True)
            
            for sheet_name in workbook.sheetnames:
                # Check if sheet name matches "Story {number}" pattern
                if sheet_name.lower().startswith('story'):
                    story_data = self._parse_sheet(workbook[sheet_name], sheet_name)
                    if story_data:
                        user_stories.append(story_data)
            
            workbook.close()
            Path(tmp_file_path).unlink()  # Delete temp file
            
            if not user_stories:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No valid user stories found in the file. Sheets should be named 'Story {number}'"
                )
            
            return user_stories
            
        except Exception as e:
            # Clean up temp file on error
            if Path(tmp_file_path).exists():
                Path(tmp_file_path).unlink()
            
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error parsing Excel file: {str(e)}"
            )
    
    def _parse_sheet(self, sheet, sheet_name: str) -> Optional[Dict[str, Any]]:
        """Parse a single sheet containing user story data"""
        try:
            # Extract story number from sheet name
            story_no = sheet_name.replace('Story', '').replace('story', '').strip()
            if not story_no:
                story_no = sheet_name
            
            story_data = {
                'story_no': f"US-{story_no.zfill(3)}",
                'title': '',
                'user_story': '',
                'story_points': '',
                'sprint': '',
                'assignee': '',
                'updated_by': '',
                'created_date': '',
                'revised_date': '',
                'acceptance_criteria': ''
            }
            
            # Parse the sheet - assuming key-value pairs format
            # Column A has field names, Column B has values
            for row in sheet.iter_rows(min_row=1, max_col=2, values_only=True):
                if row[0] and row[1]:
                    field_name = str(row[0]).strip().lower()
                    field_value = str(row[1]).strip()
                    
                    # Map field names to story_data keys
                    if 'title' in field_name or field_name.startswith('user story'):
                        if 'user story 1' in field_name.lower() or 'title' in field_name.lower():
                            story_data['title'] = field_value
                    elif field_name == 'user story':
                        story_data['user_story'] = field_value
                    elif 'story points' in field_name or 'points' in field_name:
                        story_data['story_points'] = field_value
                    elif 'sprint' in field_name:
                        story_data['sprint'] = field_value
                    elif 'assignee' in field_name:
                        story_data['assignee'] = field_value
                    elif 'updated by' in field_name:
                        story_data['updated_by'] = field_value
                    elif 'created date' in field_name:
                        story_data['created_date'] = field_value
                    elif 'revised date' in field_name:
                        story_data['revised_date'] = field_value
                    elif 'acceptance criteria' in field_name:
                        # Acceptance criteria might span multiple rows
                        story_data['acceptance_criteria'] = field_value
            
            # Validate that we have at least a user story
            if story_data['user_story'] or story_data['title']:
                return story_data
            
            return None
            
        except Exception as e:
            print(f"Error parsing sheet {sheet_name}: {str(e)}")
            return None
    
    def validate_user_stories(self, stories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate parsed user stories"""
        valid_stories = []
        errors = []
        duplicates_count = 0
        seen_story_nos = set()
        
        for story in stories:
            story_no = story.get('story_no', '')
            
            # Check for duplicates
            if story_no in seen_story_nos:
                duplicates_count += 1
                errors.append(f"Duplicate story number: {story_no}")
                continue
            
            # Validate required fields
            if not story.get('user_story') and not story.get('title'):
                errors.append(f"{story_no}: Missing user story description")
                continue
            
            seen_story_nos.add(story_no)
            valid_stories.append(story)
        
        return {
            'valid': valid_stories,
            'total': len(stories),
            'valid_count': len(valid_stories),
            'duplicates': duplicates_count,
            'errors': errors
        }

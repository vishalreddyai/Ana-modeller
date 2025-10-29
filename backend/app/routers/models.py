from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from ..models.model import Model, ModelCreate
from ..services.model_service import ModelService

router = APIRouter()
model_service = ModelService()


@router.get("/", response_model=List[Model])
def list_models(user_id: str = Query(..., description="Identifier of the current user")):
    """
    Retrieve all models created by a specific user.
    """
    return model_service.list_models(user_id=user_id)


@router.post("/", response_model=Model, status_code=status.HTTP_201_CREATED)
def create_model(model: ModelCreate):
    """
    Create a new model for the specified user.
    """
    try:
        return model_service.create_model(model)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create model",
        ) from exc


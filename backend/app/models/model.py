from typing import Optional

from pydantic import BaseModel, Field


class ModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1024)


class ModelCreate(ModelBase):
    user_id: str = Field(..., min_length=1)


class Model(ModelBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

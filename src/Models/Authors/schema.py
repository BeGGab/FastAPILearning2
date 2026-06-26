import uuid
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, List, Dict

from src.models.authors.model import BiographyAuthor


class SBiographerCreate(BaseModel):
    author_id: uuid.UUID = Field(..., description="ID автора")
    text: str = Field(..., description="Текст биографии")
    year_of_birth: int = Field(..., description="Год рождения")
    year_of_death: int = Field(..., description="Год смерти")

    model_config = ConfigDict(from_attributes=True)

    def to_orm_model(self) -> BiographyAuthor:
        return BiographyAuthor(**self.model_dump())


class SBiographerRead(BaseModel):
    id: uuid.UUID = Field(..., description="ID биографии")
    author_id: uuid.UUID = Field(..., description="ID автора")
    text: str = Field(..., description="Текст биографии")
    year_of_birth: int = Field(..., description="Год рождения")
    year_of_death: int = Field(..., description="Год смерти")

    model_config = ConfigDict(from_attributes=True)


class SBiographerUpdate(BaseModel):
    text: Optional[str] = Field(None, description="Текст биографии")
    year_of_birth: Optional[int] = Field(None, description="Год рождения")
    year_of_death: Optional[int] = Field(None, description="Год смерти")

    @model_validator(mode="after")
    def validate_update_data(self) -> "SBiographerUpdate":
        update_fields = self.model_dump(exclude_unset=True, exclude_none=True)
        if not update_fields:
            raise ValueError("Нет данных для обновления")
        return self

    def apply_updates(self, biography: BiographyAuthor) -> None:
        update_data = self.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in update_data.items():
            setattr(biography, field, value)

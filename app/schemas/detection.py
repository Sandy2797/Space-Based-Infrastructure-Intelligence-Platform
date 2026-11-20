
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PointGeometry(BaseModel):
    type: Literal["Point"]
    coordinates: tuple[float, float]


class DetectionCreate(BaseModel):
    before_image_id: int = Field(gt=0)
    after_image_id: int = Field(gt=0)

    observed_at: datetime

    geometry: PointGeometry

    origin_category: Literal[
        "human_made",
        "natural",
        "uncertain"
    ]

    confidence: float = Field(ge=0, le=1)

    model_version: str = Field(min_length=1)


class DetectionResponse(DetectionCreate):
    id: str

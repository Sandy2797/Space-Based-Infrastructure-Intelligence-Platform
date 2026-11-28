from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PointGeometry(BaseModel):
    type: Literal["Point"]
    coordinates: tuple[float, float]


class PolygonGeometry(BaseModel):
    type: Literal["Polygon"]
    coordinates: list[list[tuple[float, float]]]


class MultiPolygonGeometry(BaseModel):
    type: Literal["MultiPolygon"]
    coordinates: list[list[list[tuple[float, float]]]]


DetectionGeometry = PointGeometry | PolygonGeometry | MultiPolygonGeometry


class DetectionCreate(BaseModel):
    before_image_id: int = Field(gt=0)
    after_image_id: int = Field(gt=0)
    observed_at: datetime

    geometry: DetectionGeometry

    component_id: int | None = Field(default=None, ge=0)
    origin_category: Literal["human_made", "natural", "uncertain"]

    confidence: float | None = Field(default=None, ge=0, le=1)
    change_score: float | None = None
    threshold: dict | None = None
    pixel_count: int | None = Field(default=None, ge=0)
    area_m2: float | None = Field(default=None, ge=0)

    evidence_quality: dict | None = None
    quality_flags: list[str] | None = None
    mask_reference: str | None = None

    model_version: str = Field(min_length=1)


class DetectionResponse(DetectionCreate):
    id: str
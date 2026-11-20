from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.detection import DetectionCreate


class MockPointPrediction(BaseModel):
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)

    origin_category: Literal[
        "human_made",
        "natural",
        "uncertain",
    ]

    confidence: float = Field(ge=0, le=1)


def prepare_detection_from_mock(
    prediction: MockPointPrediction,
    *,
    before_image_id: int,
    after_image_id: int,
    observed_at: datetime,
    model_version: str = "mock-v0",
) -> DetectionCreate:

    if observed_at.tzinfo is None:
        raise ValueError(
            "observed_at must include timezone information"
        )

    return DetectionCreate(
        before_image_id=before_image_id,
        after_image_id=after_image_id,
        observed_at=observed_at,
        geometry={
            "type": "Point",
            "coordinates": [
                prediction.longitude,
                prediction.latitude,
            ],
        },
        origin_category=prediction.origin_category,
        confidence=prediction.confidence,
        model_version=model_version,
    )
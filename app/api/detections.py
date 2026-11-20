
from uuid import uuid4

from fastapi import APIRouter

from app.schemas.detection import (
    DetectionCreate,
    DetectionResponse,
)

router = APIRouter(
    prefix="/api/v1/detections",
    tags=["Detections"],
)

# Temporary storage until PostgreSQL is available.
mock_detections: list[DetectionResponse] = []


@router.post(
    "",
    response_model=DetectionResponse,
    status_code=201,
)
def create_detection(detection: DetectionCreate):
    record = DetectionResponse(
        id=str(uuid4()),
        **detection.model_dump(),
    )

    mock_detections.append(record)

    return record


@router.get(
    "",
    response_model=list[DetectionResponse],
)
def get_detections():
    return mock_detections

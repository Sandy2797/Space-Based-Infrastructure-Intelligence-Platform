
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.api.images import mock_images

from app.schemas.detection import (
    DetectionCreate,
    DetectionResponse,
)


router = APIRouter(
    prefix="/api/v1/detections",
    tags=["Detections"],
)


mock_detections: list[DetectionResponse] = []


@router.post(
    "",
    response_model=DetectionResponse,
    status_code=201,
)
def create_detection(detection: DetectionCreate):

    # A detection must compare two different images.
    if detection.before_image_id == detection.after_image_id:
        raise HTTPException(
            status_code=422,
            detail="Before and after images must be different",
        )

    # Collect registered image IDs.
    registered_ids = {
        image.id for image in mock_images
    }

    # Verify the before-image.
    if detection.before_image_id not in registered_ids:
        raise HTTPException(
            status_code=404,
            detail="Before-image not found",
        )

    # Verify the after-image.
    if detection.after_image_id not in registered_ids:
        raise HTTPException(
            status_code=404,
            detail="After-image not found",
        )

    # Create the detection.
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

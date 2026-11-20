
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


    # Retrieve the registered image records.
    image_by_id = {
        image.id: image
        for image in mock_images
    }

    before_image = image_by_id[
        detection.before_image_id
    ]

    after_image = image_by_id[
        detection.after_image_id
    ]

    # Both images must belong to the same monitoring area.
    if before_image.monitoring_area_id != after_image.monitoring_area_id:
        raise HTTPException(
            status_code=422,
            detail="Images belong to different monitoring areas",
        )

    # The before-image must be older.
    if before_image.acquired_at >= after_image.acquired_at:
        raise HTTPException(
            status_code=422,
            detail="Before-image must be older than after-image",
        )

    # Both images must have compatible CRS information.
    if before_image.crs != after_image.crs:
        raise HTTPException(
            status_code=422,
            detail="Images have different coordinate reference systems",
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

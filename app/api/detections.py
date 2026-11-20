from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.satellite_image import SatelliteImageDB
from app.schemas.detection import (
    DetectionCreate,
    DetectionResponse,
)


router = APIRouter(
    prefix="/api/v1/detections",
    tags=["Detections"],
)


# Detection storage is still temporary.
# We will migrate it to SQLite in the next milestone.
mock_detections: list[DetectionResponse] = []


@router.post(
    "",
    response_model=DetectionResponse,
    status_code=201,
)
def create_detection(
    detection: DetectionCreate,
    db: Session = Depends(get_db),
):
    # A detection must compare two different images.
    if detection.before_image_id == detection.after_image_id:
        raise HTTPException(
            status_code=422,
            detail="Before and after images must be different",
        )

    # Retrieve the before-image from the database.
    before_image = db.get(
        SatelliteImageDB,
        detection.before_image_id,
    )

    if before_image is None:
        raise HTTPException(
            status_code=404,
            detail="Before-image not found",
        )

    # Retrieve the after-image from the database.
    after_image = db.get(
        SatelliteImageDB,
        detection.after_image_id,
    )

    if after_image is None:
        raise HTTPException(
            status_code=404,
            detail="After-image not found",
        )

    # Both images must belong to the same monitoring area.
    if (
        before_image.monitoring_area_id
        != after_image.monitoring_area_id
    ):
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
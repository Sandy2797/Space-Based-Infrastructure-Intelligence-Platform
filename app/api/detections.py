from datetime import timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.detection import DetectionDB
from app.models.satellite_image import SatelliteImageDB
from app.schemas.detection import (
    DetectionCreate,
    DetectionResponse,
)


router = APIRouter(
    prefix="/api/v1/detections",
    tags=["Detections"],
)


def to_detection_response(
    record: DetectionDB,
) -> DetectionResponse:
    observed_at = record.observed_at

    # SQLite may return UTC timestamps without timezone information.
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(
            tzinfo=timezone.utc
        )

    return DetectionResponse(
        id=record.id,
        before_image_id=record.before_image_id,
        after_image_id=record.after_image_id,
        observed_at=observed_at,
        geometry=record.geometry,
        origin_category=record.origin_category,
        confidence=record.confidence,
        model_version=record.model_version,
    )


@router.post(
    "",
    response_model=DetectionResponse,
    status_code=201,
)
def create_detection(
    detection: DetectionCreate,
    db: Session = Depends(get_db),
):
    # The images must be different.
    if detection.before_image_id == detection.after_image_id:
        raise HTTPException(
            status_code=422,
            detail="Before and after images must be different",
        )

    before_image = db.get(
        SatelliteImageDB,
        detection.before_image_id,
    )

    if before_image is None:
        raise HTTPException(
            status_code=404,
            detail="Before-image not found",
        )

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

    # Both images must use the same coordinate reference system.
    if before_image.crs != after_image.crs:
        raise HTTPException(
            status_code=422,
            detail="Images have different coordinate reference systems",
        )

    # Require an explicit timezone for observation timestamps.
    if detection.observed_at.tzinfo is None:
        raise HTTPException(
            status_code=422,
            detail="observed_at must include timezone information",
        )

    record = DetectionDB(
        id=str(uuid4()),
        before_image_id=detection.before_image_id,
        after_image_id=detection.after_image_id,
        observed_at=detection.observed_at.astimezone(
            timezone.utc
        ),
        geometry=detection.geometry.model_dump(),
        origin_category=detection.origin_category,
        confidence=detection.confidence,
        model_version=detection.model_version,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return to_detection_response(record)


@router.get(
    "",
    response_model=list[DetectionResponse],
)
def get_detections(
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(DetectionDB).order_by(
            DetectionDB.observed_at,
            DetectionDB.id,
        )
    ).all()

    return [
        to_detection_response(record)
        for record in records
    ]
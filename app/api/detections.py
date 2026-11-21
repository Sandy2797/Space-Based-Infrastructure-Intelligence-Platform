from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from uuid import uuid4
from app.db.spatial import from_storage, to_storage
from fastapi import APIRouter, Depends, HTTPException, Query
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
        geometry=from_storage(record.geometry),
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
        geometry=to_storage(
    detection.geometry.model_dump(),
    db,
),
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
    monitoring_area_id: int | None = Query(default=None, gt=0),
    origin_category: Literal[
        "human_made",
        "natural",
        "uncertain",
    ] | None = None,
    min_confidence: float | None = Query(
        default=None, ge=0, le=1
    ),
    max_confidence: float | None = Query(
        default=None, ge=0, le=1
    ),
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    # Validate confidence range.
    if (
        min_confidence is not None
        and max_confidence is not None
        and min_confidence > max_confidence
    ):
        raise HTTPException(
            status_code=422,
            detail="Minimum confidence cannot exceed maximum confidence",
        )

    # Validate date range.
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=422,
            detail="Start date cannot be after end date",
        )

    statement = (
        select(DetectionDB)
        .join(
            SatelliteImageDB,
            DetectionDB.before_image_id == SatelliteImageDB.id,
        )
    )

    # Filter by monitoring area.
    if monitoring_area_id is not None:
        statement = statement.where(
            SatelliteImageDB.monitoring_area_id
            == monitoring_area_id
        )

    # Filter by detection category.
    if origin_category is not None:
        statement = statement.where(
            DetectionDB.origin_category == origin_category
        )

    # Filter by minimum confidence.
    if min_confidence is not None:
        statement = statement.where(
            DetectionDB.confidence >= min_confidence
        )

    # Filter by maximum confidence.
    if max_confidence is not None:
        statement = statement.where(
            DetectionDB.confidence <= max_confidence
        )

    # Dates are interpreted as UTC.
    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            time.min,
            tzinfo=timezone.utc,
        )
        statement = statement.where(
            DetectionDB.observed_at >= start_datetime
        )

    if end_date is not None:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )
        statement = statement.where(
            DetectionDB.observed_at < end_datetime
        )

    records = db.scalars(
        statement.order_by(
            DetectionDB.observed_at,
            DetectionDB.id,
        )
    ).all()

    return [
        to_detection_response(record)
        for record in records
    ]
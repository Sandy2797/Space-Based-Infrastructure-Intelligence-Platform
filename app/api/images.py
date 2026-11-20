from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.satellite_image import SatelliteImageDB
from app.schemas.satellite_image import (
    SatelliteImageCreate,
    SatelliteImageResponse,
)


router = APIRouter(
    prefix="/api/v1/images",
    tags=["Satellite Images"],
)


def to_image_response(
    record: SatelliteImageDB,
) -> SatelliteImageResponse:
    """Convert a database record to an API response."""

    acquired_at = record.acquired_at

    # SQLite may return timestamps without timezone information.
    # Images are stored using UTC, so restore UTC when necessary.
    if acquired_at.tzinfo is None:
        acquired_at = acquired_at.replace(
            tzinfo=timezone.utc
        )

    return SatelliteImageResponse(
        id=record.id,
        monitoring_area_id=record.monitoring_area_id,
        provider=record.provider,
        file_reference=record.file_reference,
        acquired_at=acquired_at,
        crs=record.crs,
        width=record.width,
        height=record.height,
        band_count=record.band_count,
    )


@router.post(
    "",
    response_model=SatelliteImageResponse,
    status_code=201,
)
def register_image(
    image: SatelliteImageCreate,
    db: Session = Depends(get_db),
):
    image_data = image.model_dump()

    # Normalize timestamps to UTC before storing them.
    image_data["acquired_at"] = (
        image.acquired_at.astimezone(timezone.utc)
    )

    record = SatelliteImageDB(**image_data)

    db.add(record)
    db.commit()
    db.refresh(record)

    return to_image_response(record)


@router.get(
    "",
    response_model=list[SatelliteImageResponse],
)
def get_images(
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(SatelliteImageDB).order_by(
            SatelliteImageDB.id
        )
    ).all()

    return [
        to_image_response(record)
        for record in records
    ]


@router.get(
    "/{image_id}",
    response_model=SatelliteImageResponse,
)
def get_image(
    image_id: int,
    db: Session = Depends(get_db),
):
    record = db.get(
        SatelliteImageDB,
        image_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Satellite image not found",
        )

    return to_image_response(record)
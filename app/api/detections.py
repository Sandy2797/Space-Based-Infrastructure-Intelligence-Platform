from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2 import Geography
from pyproj import CRS, Transformer
from shapely.geometry import shape
from shapely import transform as transform_shape
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.spatial import from_storage, to_storage
from app.models.monitoring_area import MonitoringAreaDB
from app.models.detection import DetectionDB
from app.models.infrastructure_asset import InfrastructureAssetDB
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
        component_id=record.component_id,
        origin_category=record.origin_category,
        confidence=record.confidence,
        change_score=record.change_score,
        threshold=record.threshold,
        pixel_count=record.pixel_count,
        area_m2=record.area_m2,
        evidence_quality=record.evidence_quality,
        quality_flags=record.quality_flags,
        mask_reference=record.mask_reference,
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
    # Require an explicit timezone for observation timestamps.
    if detection.observed_at.tzinfo is None:
        raise HTTPException(
            status_code=422,
            detail="observed_at must include timezone information",
        )

    # Retrieve the monitoring area associated with the images.
    monitoring_area = db.get(
        MonitoringAreaDB,
        before_image.monitoring_area_id,
    )

    if monitoring_area is None:
        raise HTTPException(
            status_code=404,
            detail="Monitoring area not found",
        )

    # Transform detection geometry into EPSG:4326.
    try:
        stored_geometry = to_storage(
            detection.geometry.model_dump(),
            db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    # Both geometries are now in EPSG:4326.
    area_geometry = shape(
        from_storage(monitoring_area.geometry)
    )

    detection_geometry = shape(
        from_storage(stored_geometry)
    )

    # Ensure the complete detection is inside its monitoring area.
    if not area_geometry.covers(detection_geometry):
        raise HTTPException(
            status_code=422,
            detail="Detection must be inside its monitoring area",
        )

    record = DetectionDB(
            id=str(uuid4()),
            before_image_id=detection.before_image_id,
            after_image_id=detection.after_image_id,
            observed_at=detection.observed_at.astimezone(timezone.utc),
            geometry=stored_geometry,
            component_id=detection.component_id,
            origin_category=detection.origin_category,
            confidence=detection.confidence,
            change_score=detection.change_score,
            threshold=detection.threshold,
            pixel_count=detection.pixel_count,
            area_m2=detection.area_m2,
            evidence_quality=detection.evidence_quality,
            quality_flags=detection.quality_flags,
            mask_reference=detection.mask_reference,
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
@router.get(
    "/near-asset/{asset_id}",
    response_model=list[DetectionResponse],
)
def get_detections_near_asset(
    asset_id: int,
    radius_m: float = Query(default=500, gt=0, le=100000),
    db: Session = Depends(get_db),
):
    # Find the infrastructure asset.
    asset = db.get(InfrastructureAssetDB, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Infrastructure asset not found",
        )

    # Get detections from the same monitoring area.
    statement = (
        select(DetectionDB)
        .join(
            SatelliteImageDB,
            DetectionDB.before_image_id == SatelliteImageDB.id,
        )
        .where(
            SatelliteImageDB.monitoring_area_id
            == asset.monitoring_area_id
        )
    )

    # Use PostGIS for PostgreSQL.
    if db.get_bind().dialect.name == "postgresql":
        statement = statement.where(
            func.ST_DWithin(
                cast(
                    DetectionDB.geometry,
                    Geography(srid=4326),
                ),
                cast(
                    InfrastructureAssetDB.location,
                    Geography(srid=4326),
                ),
                radius_m,
            )
        ).join(
            InfrastructureAssetDB,
            InfrastructureAssetDB.id == asset_id,
        )

        records = db.scalars(statement).all()

    else:
        # Use metric distance calculations for SQLite tests.
        asset_geometry = shape(from_storage(asset.location))

        center = asset_geometry.centroid

        local_crs = CRS.from_proj4(
            f"+proj=aeqd +lat_0={center.y} "
            f"+lon_0={center.x} +datum=WGS84 +units=m +no_defs"
        )

        transformer = Transformer.from_crs(
            "EPSG:4326",
            local_crs,
            always_xy=True,
        )

        project = transformer.transform

        projected_asset = transform_shape(
            asset_geometry,
            project,
            interleaved=False,
)

        records = db.scalars(
            statement.order_by(
                DetectionDB.observed_at,
                DetectionDB.id,
            )
        ).all()

        records = [
            record
            for record in records
            if transform_shape(
                shape(from_storage(record.geometry)),
                project,
                interleaved=False,
            ).distance(projected_asset) <= radius_m
        ]

    return [
        to_detection_response(record)
        for record in records
    ]
from math import isfinite

from fastapi import APIRouter, Depends, HTTPException, Query
from shapely.geometry import box, shape
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db.spatial import (
    STORAGE_CRS,
    from_storage,
    to_storage,
)
from app.db.database import get_db
from app.models.infrastructure_asset import InfrastructureAssetDB
from app.models.monitoring_area import MonitoringAreaDB
from app.schemas.infrastructure_asset import (
    InfrastructureAssetCreate,
    InfrastructureAssetResponse,
)


router = APIRouter(
    prefix="/api/v1/infrastructure-assets",
    tags=["Infrastructure Assets"],
)


def to_asset_response(
    record: InfrastructureAssetDB,
) -> InfrastructureAssetResponse:
    return InfrastructureAssetResponse(
        id=record.id,
        monitoring_area_id=record.monitoring_area_id,
        asset_name=record.asset_name,
        asset_type=record.asset_type,
        location=from_storage(record.location),
        location_crs=STORAGE_CRS,
    )

@router.post(
    "",
    response_model=InfrastructureAssetResponse,
    status_code=201,
)
def create_infrastructure_asset(
    asset: InfrastructureAssetCreate,
    db: Session = Depends(get_db),
):
    monitoring_area = db.get(
        MonitoringAreaDB,
        asset.monitoring_area_id,
    )

    if monitoring_area is None:
        raise HTTPException(
            status_code=404,
            detail="Monitoring area not found",
        )

    # Transform asset geometry into EPSG:4326.
    try:
        stored_location = to_storage(
            asset.location,
            db,
            source_crs=asset.crs,
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

    asset_geometry = shape(
        from_storage(stored_location)
    )

    # Ensure the transformed asset is inside its monitoring area.
    if not area_geometry.covers(asset_geometry):
        raise HTTPException(
            status_code=422,
            detail="Infrastructure asset must be inside its monitoring area",
        )

    record = InfrastructureAssetDB(
        monitoring_area_id=asset.monitoring_area_id,
        asset_name=asset.asset_name,
        asset_type=asset.asset_type,
        location=stored_location,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return to_asset_response(record)

@router.get(
    "",
    response_model=list[InfrastructureAssetResponse],
)
def get_infrastructure_assets(
    monitoring_area_id: int | None = Query(
        default=None,
        gt=0,
    ),
    asset_type: str | None = Query(
        default=None,
        min_length=1,
        max_length=80,
    ),
    bbox: str | None = Query(
        default=None,
        description="Bounding box: west,south,east,north",
    ),
    db: Session = Depends(get_db),
):
    statement = select(InfrastructureAssetDB)

    # Filter by monitoring area.
    if monitoring_area_id is not None:
        statement = statement.where(
            InfrastructureAssetDB.monitoring_area_id
            == monitoring_area_id
        )

    # Filter by asset type.
    if asset_type is not None:
        normalized_type = asset_type.strip()

        if not normalized_type:
            raise HTTPException(
                status_code=422,
                detail="Asset type cannot be empty",
            )

        statement = statement.where(
            func.lower(InfrastructureAssetDB.asset_type)
            == normalized_type.lower()
        )

    search_area = None

    # Validate bounding-box coordinates.
    if bbox is not None:
        try:
            coordinates = [
                float(value.strip())
                for value in bbox.split(",")
            ]
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail="Invalid bbox. Use west,south,east,north",
            ) from exc

        if len(coordinates) != 4:
            raise HTTPException(
                status_code=422,
                detail="bbox must contain exactly four coordinates",
            )

        west, south, east, north = coordinates

        if not all(isfinite(value) for value in coordinates):
            raise HTTPException(
                status_code=422,
                detail="Bounding box coordinates must be finite",
            )

        if not (
            -180 <= west < east <= 180
            and -90 <= south < north <= 90
        ):
            raise HTTPException(
                status_code=422,
                detail="Invalid geographic bounding box",
            )

        # PostgreSQL: filter directly using PostGIS.
        if db.get_bind().dialect.name == "postgresql":
            statement = statement.where(
                func.ST_Intersects(
                    InfrastructureAssetDB.location,
                    func.ST_MakeEnvelope(
                        west,
                        south,
                        east,
                        north,
                        4326,
                    ),
                )
            )

        # SQLite: retain Shapely filtering.
        else:
            search_area = box(
                west,
                south,
                east,
                north,
            )

    # Execute database query after applying SQL filters.
    records = db.scalars(
        statement.order_by(InfrastructureAssetDB.id)
    ).all()

    # Apply Shapely filtering for SQLite.
    if search_area is not None:
        records = [
            record
            for record in records
            if shape(
                from_storage(record.location)
            ).intersects(search_area)
        ]

    return [
        to_asset_response(record)
        for record in records
    ]


@router.get(
    "/{asset_id}",
    response_model=InfrastructureAssetResponse,
)
def get_infrastructure_asset(
    asset_id: int,
    db: Session = Depends(get_db),
):
    record = db.get(
        InfrastructureAssetDB,
        asset_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Infrastructure asset not found",
        )

    return to_asset_response(record)

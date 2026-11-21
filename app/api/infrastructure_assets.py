
from fastapi import APIRouter, Depends, HTTPException
from shapely.geometry import shape
from sqlalchemy import select
from sqlalchemy.orm import Session

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
        location=record.location,
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
    # Check that the monitoring area exists.
    monitoring_area = db.get(
        MonitoringAreaDB,
        asset.monitoring_area_id,
    )

    if monitoring_area is None:
        raise HTTPException(
            status_code=404,
            detail="Monitoring area not found",
        )

    # Convert GeoJSON into Shapely geometries.
    area_geometry = shape(
        monitoring_area.geometry
    )

    asset_geometry = shape(
        asset.location
    )

    # Ensure the complete asset geometry is inside
    # its assigned monitoring area.
    if not area_geometry.covers(asset_geometry):
        raise HTTPException(
            status_code=422,
            detail="Infrastructure asset must be inside its monitoring area",
        )

    # Create the database record.
    record = InfrastructureAssetDB(
        monitoring_area_id=asset.monitoring_area_id,
        asset_name=asset.asset_name,
        asset_type=asset.asset_type,
        location=asset.location,
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
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(InfrastructureAssetDB).order_by(
            InfrastructureAssetDB.id
        )
    ).all()

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

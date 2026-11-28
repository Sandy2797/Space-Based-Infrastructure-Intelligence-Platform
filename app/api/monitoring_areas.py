
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.spatial import (
    STORAGE_CRS,
    from_storage,
    to_storage,
)
from app.db.database import get_db
from app.models.monitoring_area import MonitoringAreaDB
from app.schemas.monitoring_area import (
    MonitoringAreaCreate,
    MonitoringAreaResponse,
)


router = APIRouter(
    prefix="/api/v1/monitoring-areas",
    tags=["Monitoring Areas"],
)


def to_area_response(
    record: MonitoringAreaDB,
) -> MonitoringAreaResponse:
    return MonitoringAreaResponse(
        id=record.id,
        name=record.name,
        crs=record.crs,
        geometry_crs=STORAGE_CRS,
        geometry=from_storage(record.geometry),
    )


@router.post(
    "",
    response_model=MonitoringAreaResponse,
    status_code=201,
)
def create_monitoring_area(
    area: MonitoringAreaCreate,
    db: Session = Depends(get_db),
):
    try:
        stored_geometry = to_storage(
            area.geometry,
            db,
            source_crs=area.crs,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    record = MonitoringAreaDB(
        name=area.name,
        crs=area.crs,
        geometry=stored_geometry,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return to_area_response(record)


@router.get(
    "",
    response_model=list[MonitoringAreaResponse],
)
def get_monitoring_areas(
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(MonitoringAreaDB).order_by(
            MonitoringAreaDB.id
        )
    ).all()

    return [
        to_area_response(record)
        for record in records
    ]


@router.get(
    "/{area_id}",
    response_model=MonitoringAreaResponse,
)
def get_monitoring_area(
    area_id: int,
    db: Session = Depends(get_db),
):
    record = db.get(
        MonitoringAreaDB,
        area_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Monitoring area not found",
        )

    return to_area_response(record)
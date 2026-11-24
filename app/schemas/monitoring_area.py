
from math import isfinite
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator
from shapely import get_coordinates
from shapely.geometry import shape

from app.db.spatial import normalize_crs, STORAGE_CRS


class MonitoringAreaCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=120,
    )

    crs: str = STORAGE_CRS

    geometry: dict[str, Any]

    @field_validator("crs")
    @classmethod
    def validate_crs(cls, value):
        return normalize_crs(value)

    @field_validator("geometry")
    @classmethod
    def validate_geometry(cls, value):
        if value.get("type") not in {
            "Polygon",
            "MultiPolygon",
        }:
            raise ValueError(
                "Monitoring area must be a Polygon or MultiPolygon"
            )

        try:
            boundary = shape(value)

        except (TypeError, ValueError, KeyError, IndexError) as exc:
            raise ValueError(
                "Invalid GeoJSON geometry"
            ) from exc

        if boundary.is_empty or not boundary.is_valid:
            raise ValueError(
                "Monitoring area geometry is empty or invalid"
            )

        coordinates = get_coordinates(boundary)

        if not all(
            isfinite(float(value))
            for row in coordinates
            for value in row
        ):
            raise ValueError(
                "Monitoring area contains non-finite coordinates"
            )

        return value


class MonitoringAreaResponse(MonitoringAreaCreate):
    id: int

    # Returned geometry is always stored in EPSG:4326.
    geometry_crs: Literal["EPSG:4326"] = "EPSG:4326"

from math import isfinite
from typing import Any, Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from shapely import get_coordinates
from shapely.geometry import shape

from app.db.spatial import STORAGE_CRS, normalize_crs


class InfrastructureAssetCreate(BaseModel):

    monitoring_area_id: int = Field(gt=0)

    asset_name: str = Field(
        min_length=1,
        max_length=120,
    )

    asset_type: str = Field(
        min_length=1,
        max_length=80,
    )

    crs: str = STORAGE_CRS

    location: dict[str, Any]

    @field_validator("crs")
    @classmethod
    def validate_crs(cls, value):
        return normalize_crs(value)

    @field_validator("asset_name", "asset_type", mode="before")
    @classmethod
    def validate_text(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("location")
    @classmethod
    def validate_location(cls, value):

        allowed_types = {
            "Point",
            "MultiPoint",
            "LineString",
            "MultiLineString",
            "Polygon",
            "MultiPolygon",
        }

        if value.get("type") not in allowed_types:
            raise ValueError(
                "Unsupported infrastructure asset geometry type"
            )

        try:
            asset_geometry = shape(value)

        except (TypeError, ValueError, KeyError, IndexError) as exc:
            raise ValueError(
                "Invalid GeoJSON geometry"
            ) from exc

        if asset_geometry.is_empty or not asset_geometry.is_valid:
            raise ValueError(
                "Infrastructure asset geometry is empty or invalid"
            )

        coordinates = get_coordinates(asset_geometry)

        if not all(
            isfinite(float(value))
            for row in coordinates
            for value in row
        ):
            raise ValueError(
                "Infrastructure asset contains non-finite coordinates"
            )

        return value


class InfrastructureAssetResponse(BaseModel):

    id: int

    monitoring_area_id: int

    asset_name: str

    asset_type: str

    location: dict[str, Any]

    location_crs: Literal["EPSG:4326"] = STORAGE_CRS

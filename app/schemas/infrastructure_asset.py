
from typing import Any

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from shapely.geometry import shape


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

    location: dict[str, Any]

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

        min_lon, min_lat, max_lon, max_lat = asset_geometry.bounds

        if not (
            -180 <= min_lon <= 180
            and -180 <= max_lon <= 180
            and -90 <= min_lat <= 90
            and -90 <= max_lat <= 90
        ):
            raise ValueError(
                "Coordinates are outside valid longitude/latitude ranges"
            )

        return value


class InfrastructureAssetResponse(InfrastructureAssetCreate):
    id: int

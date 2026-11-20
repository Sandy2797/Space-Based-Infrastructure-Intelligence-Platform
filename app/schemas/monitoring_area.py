from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator
from shapely.geometry import shape


class MonitoringAreaCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=120,
    )

    crs: Literal["EPSG:4326"] = "EPSG:4326"

    geometry: dict[str, Any]

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

        # GeoJSON coordinates use longitude, latitude order.
        min_lon, min_lat, max_lon, max_lat = boundary.bounds

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


class MonitoringAreaResponse(MonitoringAreaCreate):
    id: int
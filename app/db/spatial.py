from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement, WKTElement
from geoalchemy2.shape import from_shape, to_shape

from shapely.geometry import mapping, shape
from sqlalchemy import JSON
from sqlalchemy.orm import Session


def geojson_column(geometry_type="GEOMETRY"):
    return JSON().with_variant(
        Geometry(
            geometry_type=geometry_type,
            srid=4326,
            spatial_index=False,
        ),
        "postgresql",
    )


def to_storage(geometry, db: Session):
    if db.get_bind().dialect.name == "postgresql":
        return from_shape(
            shape(geometry),
            srid=4326,
        )

    return geometry


def from_storage(geometry):
    if isinstance(geometry, (WKBElement, WKTElement)):
        return mapping(to_shape(geometry))

    return geometry
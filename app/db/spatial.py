
from math import isfinite

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement, WKTElement
from geoalchemy2.shape import from_shape, to_shape

from pyproj import CRS, Transformer
from pyproj.exceptions import CRSError, ProjError

from shapely import get_coordinates
from shapely import has_z, transform as shapely_transform
from shapely.geometry import mapping, shape

from sqlalchemy import JSON
from sqlalchemy.orm import Session


STORAGE_CRS = "EPSG:4326"


def normalize_crs(crs: str) -> str:
    """
    Validate and normalize a geographic or projected CRS.
    """
    try:
        parsed_crs = CRS.from_user_input(crs)
    except (CRSError, TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid coordinate reference system: {crs}"
        ) from exc

    if not (
        parsed_crs.is_geographic
        or parsed_crs.is_projected
    ):
        raise ValueError(
            "Only geographic and projected CRS values are supported"
        )

    authority = parsed_crs.to_authority()

    if authority:
        return f"{authority[0]}:{authority[1]}"

    return parsed_crs.to_string()


def transform_geometry(
    geometry,
    source_crs: str,
    target_crs: str = STORAGE_CRS,
):
    """
    Transform geometry coordinates from source CRS
    into the target CRS.

    Always uses longitude/easting first (x),
    latitude/northing second (y).
    """

    try:
        source = CRS.from_user_input(source_crs)
        target = CRS.from_user_input(target_crs)

    except (CRSError, TypeError, ValueError) as exc:
        raise ValueError(
            "Invalid source or target CRS"
        ) from exc

    if not (
        source.is_geographic or source.is_projected
    ):
        raise ValueError(
            "Unsupported source CRS"
        )

    if not (
        target.is_geographic or target.is_projected
    ):
        raise ValueError(
            "Unsupported target CRS"
        )

    try:
        geom = shape(geometry)

        if geom.is_empty or not geom.is_valid:
            raise ValueError(
                "Input geometry is empty or invalid"
            )

        # Transform only when source and target CRS differ.
        if source != target:

            transformer = Transformer.from_crs(
                source,
                target,
                always_xy=True,
            )

            # Handle 3D geometries.
            if has_z(geom):

                geom = shapely_transform(
                    geom,
                    lambda x, y, z: transformer.transform(
                        x, y, z, errcheck=True
                    ),
                    include_z=True,
                    interleaved=False,
                )

            # Handle 2D geometries.
            else:

                geom = shapely_transform(
                    geom,
                    lambda x, y: transformer.transform(
                        x, y, errcheck=True
                    ),
                    interleaved=False,
                )

        # If both CRS values are identical,
        # keep the original geometry unchanged.

        if geom.is_empty or not geom.is_valid:
            raise ValueError(
                "Transformed geometry is empty or invalid"
            )

        coordinates = get_coordinates(geom)

        if not all(
            isfinite(float(value))
            for row in coordinates
            for value in row
        ):
            raise ValueError(
                "Transformed geometry contains non-finite coordinates"
            )

        # Validate geographic coordinates when storing in WGS84.
        if target == CRS.from_epsg(4326):

            west, south, east, north = geom.bounds

            if not (
                -180 <= west <= 180
                and -180 <= east <= 180
                and -90 <= south <= 90
                and -90 <= north <= 90
            ):
                raise ValueError(
                    "Transformed coordinates are outside EPSG:4326 ranges"
                )

        return geom

    except ProjError as exc:
        raise ValueError(
            "Coordinate transformation failed"
        ) from exc


def geojson_column(geometry_type="GEOMETRY"):
    """
    Use JSON for SQLite and native PostGIS geometry
    for PostgreSQL.
    """
    return JSON().with_variant(
        Geometry(
            geometry_type=geometry_type,
            srid=4326,
            spatial_index=False,
        ),
        "postgresql",
    )


def to_storage(
    geometry,
    db: Session,
    source_crs: str = STORAGE_CRS,
):
    """
    Transform geometry to EPSG:4326 before storage.
    """

    transformed = transform_geometry(
        geometry,
        source_crs,
        STORAGE_CRS,
    )

    if db.get_bind().dialect.name == "postgresql":

        return from_shape(
            transformed,
            srid=4326,
        )

    return mapping(transformed)


def from_storage(geometry):
    """
    Convert database geometry into GeoJSON-compatible data.
    """

    if isinstance(geometry, (WKBElement, WKTElement)):

        return mapping(
            to_shape(geometry)
        )

    return geometry

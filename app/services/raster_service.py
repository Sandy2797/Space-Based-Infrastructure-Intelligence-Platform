
from math import isfinite
from pathlib import Path

import rasterio
from rasterio.errors import RasterioError
from rasterio.warp import transform_bounds


def read_image_metadata(file_path: str | Path) -> dict:
    """
    Read geospatial metadata from a satellite raster image.

    The original image is never modified.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Satellite image not found: {path}"
        )

    try:
        with rasterio.open(path) as image:

            # Validate raster dimensions.
            if image.width <= 0 or image.height <= 0:
                raise ValueError(
                    "Raster dimensions must be positive"
                )

            # Validate the number of bands.
            if image.count <= 0:
                raise ValueError(
                    "Raster must contain at least one band"
                )

            # Validate the geospatial transformation.
            transform = list(image.transform)[:6]

            if not all(isfinite(value) for value in transform):
                raise ValueError(
                    "Raster has an invalid or degenerate geospatial transform"
                )

            a, b, c, d, e, f = transform

            # A zero determinant means the transformation
            # cannot be inverted.
            determinant = a * e - b * d

            if determinant == 0:
                raise ValueError(
                    "Raster has an invalid or degenerate geospatial transform"
                )

            metadata = {
                "filename": path.name,
                "format": image.driver,
                "width": image.width,
                "height": image.height,
                "band_count": image.count,
                "crs": (
                    image.crs.to_string()
                    if image.crs
                    else None
                ),
                "bounds": {
                    "left": image.bounds.left,
                    "bottom": image.bounds.bottom,
                    "right": image.bounds.right,
                    "top": image.bounds.top,
                },
                "pixel_size": {
                    "x": image.res[0],
                    "y": image.res[1],
                },
                "data_type": (
                    image.dtypes[0]
                    if image.count
                    else None
                ),
                "nodata": image.nodata,
                "transform": transform,
            }

            # Convert geographic bounds to EPSG:4326.
            if image.crs:
                west, south, east, north = transform_bounds(
                    image.crs,
                    "EPSG:4326",
                    *image.bounds,
                )

                metadata["bounds_wgs84"] = {
                    "left": west,
                    "bottom": south,
                    "right": east,
                    "top": north,
                }
            else:
                metadata["bounds_wgs84"] = None

        return metadata

    except RasterioError as exc:
        raise ValueError(
            f"Unsupported or unreadable raster file: {path}"
        ) from exc

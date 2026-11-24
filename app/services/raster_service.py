
from pathlib import Path
from rasterio.warp import transform_bounds
import rasterio


def read_image_metadata(file_path: str | Path) -> dict:
    """
    Read geospatial metadata from a satellite raster image.

    This function does not modify the original image.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Satellite image not found: {path}"
        )

    with rasterio.open(path) as image:
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
            "transform": list(image.transform)[:6],
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

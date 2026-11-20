
import numpy as np
import pytest
import rasterio

from rasterio.transform import from_origin

from app.services.raster_service import read_image_metadata


def test_read_image_metadata(tmp_path):
    # Create a temporary synthetic GeoTIFF
    image_path = tmp_path / "sample.tif"

    image_data = np.zeros(
        (8, 10),
        dtype=np.uint8
    )

    with rasterio.open(
        image_path,
        "w",
        driver="GTiff",
        height=8,
        width=10,
        count=1,
        dtype="uint8",
        crs="EPSG:4326",
        transform=from_origin(
            31.0,
            30.0,
            0.01,
            0.01
        ),
    ) as image:
        image.write(image_data, 1)

    # Read the image using our service
    result = read_image_metadata(image_path)

    # Verify the extracted information
    assert result["filename"] == "sample.tif"
    assert result["width"] == 10
    assert result["height"] == 8
    assert result["band_count"] == 1
    assert result["crs"] == "EPSG:4326"
    assert result["format"] == "GTiff"


def test_missing_image(tmp_path):
    missing_path = tmp_path / "missing.tif"

    with pytest.raises(FileNotFoundError):
        read_image_metadata(missing_path)

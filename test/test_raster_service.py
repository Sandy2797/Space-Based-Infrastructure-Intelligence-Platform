from datetime import datetime, timezone

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from app.services.raster_service import read_image_metadata
from app.services.image_registration import prepare_image_registration


def test_raster_metadata_and_crs_conversion(tmp_path):
    image_path = tmp_path / "test_3857.tif"

    with rasterio.open(
        image_path,
        "w",
        driver="GTiff",
        width=3,
        height=2,
        count=1,
        dtype="uint8",
        crs="EPSG:3857",
        transform=from_origin(
            3450000, 3500000, 100, 100
        ),
        nodata=0,
    ) as image:
        image.write(np.ones((1, 2, 3), dtype=np.uint8))

    metadata = read_image_metadata(image_path)

    assert metadata["width"] == 3
    assert metadata["height"] == 2
    assert metadata["band_count"] == 1
    assert metadata["crs"] == "EPSG:3857"
    assert metadata["nodata"] == 0

    assert metadata["transform"] == [
        100, 0, 3450000,
        0, -100, 3500000,
    ]

    bounds = metadata["bounds_wgs84"]

    assert bounds is not None
    assert -180 <= bounds["left"] < bounds["right"] <= 180
    assert -90 <= bounds["bottom"] < bounds["top"] <= 90


def test_missing_crs_is_rejected(tmp_path):
    image_path = tmp_path / "no_crs.tif"

    with rasterio.open(
        image_path,
        "w",
        driver="GTiff",
        width=2,
        height=2,
        count=1,
        dtype="uint8",
        transform=from_origin(31, 30, 0.01, 0.01),
    ) as image:
        image.write(np.ones((1, 2, 2), dtype=np.uint8))

    metadata = read_image_metadata(image_path)

    assert metadata["crs"] is None
    assert metadata["bounds_wgs84"] is None

    with pytest.raises(ValueError, match="no coordinate reference system"):
        prepare_image_registration(
            file_path=image_path,
            monitoring_area_id=1,
            provider="synthetic_test_data",
            acquired_at=datetime.now(timezone.utc),
        )


def test_missing_raster_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_image_metadata(tmp_path / "missing.tif")

def test_read_image_metadata(tmp_path):
    image_path = tmp_path / "sample.tif"

    image_data = np.zeros(
        (8, 10),
        dtype=np.uint8,
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
            31.0, 30.0, 0.01, 0.01
        ),
    ) as image:
        image.write(image_data, 1)

    result = read_image_metadata(image_path)

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

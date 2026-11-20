import numpy as np
import rasterio
from fastapi.testclient import TestClient
from rasterio.transform import from_origin
from app.main import app
from app.services.image_registration import prepare_image_registration
from datetime import datetime, timezone


client = TestClient(app)


def test_prepare_and_register_image(tmp_path):

    # Create a temporary synthetic GeoTIFF.
    image_path = tmp_path / "synthetic.tif"

    image_data = np.zeros(
        (1, 8, 10),
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
            31.0,
            30.0,
            0.01,
            0.01,
        ),
    ) as image:
        image.write(image_data)

    # Extract metadata and prepare registration.
    registration = prepare_image_registration(
        file_path=image_path,
        monitoring_area_id=1,
        provider="synthetic_test_data",
        acquired_at=datetime(
            2026, 11, 20,
            tzinfo=timezone.utc,
        ),
    )

    assert registration.width == 10
    assert registration.height == 8
    assert registration.band_count == 1
    assert registration.crs == "EPSG:4326"

    # Register the extracted metadata using the API.
    response = client.post(
        "/api/v1/images",
        json=registration.model_dump(mode="json"),
    )

    assert response.status_code == 201
    assert response.json()["width"] == 10
    assert response.json()["band_count"] == 1


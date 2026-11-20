
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.api.images import mock_images


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_images():
    mock_images.clear()
    yield
    mock_images.clear()


def sample_image():
    return {
        "monitoring_area_id": 1,
        "provider": "synthetic_test_data",
        "file_reference": "samples/image_before.tif",
        "acquired_at": "2026-11-01T10:00:00Z",
        "crs": "EPSG:4326",
        "width": 1024,
        "height": 1024,
        "band_count": 3,
    }


def test_register_image():
    response = client.post(
        "/api/v1/images",
        json=sample_image(),
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_get_images():
    client.post(
        "/api/v1/images",
        json=sample_image(),
    )

    response = client.get("/api/v1/images")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_image_not_found():
    response = client.get("/api/v1/images/999")

    assert response.status_code == 404


def test_invalid_image_dimensions():
    image = sample_image()
    image["width"] = 0

    response = client.post(
        "/api/v1/images",
        json=image,
    )

    assert response.status_code == 422


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def sample_image(monitoring_area_id=1):
    return {
        "monitoring_area_id": monitoring_area_id,
        "provider": "synthetic_test_data",
        "file_reference": "samples/image_before.tif",
        "acquired_at": "2026-11-01T10:00:00Z",
        "crs": "EPSG:4326",
        "width": 1024,
        "height": 1024,
        "band_count": 3,
    }


def test_register_image(monitoring_area):
    response = client.post(
        "/api/v1/images",
        json=sample_image(monitoring_area),
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_get_images(monitoring_area):
    client.post(
        "/api/v1/images",
        json=sample_image(monitoring_area),
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


def test_registered_image_is_retrievable(monitoring_area):
    registration = client.post(
        "/api/v1/images",
        json=sample_image(monitoring_area),
    )

    assert registration.status_code == 201

    image_id = registration.json()["id"]

    response = client.get(
        f"/api/v1/images/{image_id}"
    )

    assert response.status_code == 200

    saved_image = response.json()

    assert saved_image["id"] == image_id
    assert saved_image["width"] == 1024
    assert saved_image["crs"] == "EPSG:4326"
    assert saved_image["file_reference"] == (
        "samples/image_before.tif"
    )


def test_register_image_with_unknown_monitoring_area_returns_404():
    response = client.post(
        "/api/v1/images",
        json=sample_image(monitoring_area_id=999),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Monitoring area not found"

import pytest

from fastapi.testclient import TestClient
from app.main import app
from app.api.detections import mock_detections


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_mock_data():
    mock_detections.clear()

    yield

    mock_detections.clear()


def sample_image(acquired_at, file_reference):
    return {
        "monitoring_area_id": 1,
        "provider": "synthetic_test_data",
        "file_reference": file_reference,
        "acquired_at": acquired_at,
        "crs": "EPSG:4326",
        "width": 1024,
        "height": 1024,
        "band_count": 3,
    }


def register_two_images():
    before = client.post(
        "/api/v1/images",
        json=sample_image(
            "2026-11-01T10:00:00Z",
            "samples/before.tif",
        ),
    )

    after = client.post(
        "/api/v1/images",
        json=sample_image(
            "2026-11-15T10:00:00Z",
            "samples/after.tif",
        ),
    )

    assert before.status_code == 201
    assert after.status_code == 201

    return before.json()["id"], after.json()["id"]


def sample_detection():
    return {
        "before_image_id": 1,
        "after_image_id": 2,
        "observed_at": "2026-11-20T10:00:00Z",
        "geometry": {
            "type": "Point",
            "coordinates": [31.2, 30.2],
        },
        "origin_category": "human_made",
        "confidence": 0.87,
        "model_version": "mock-v0",
    }


def test_create_and_get_detection():
    before_id, after_id = register_two_images()

    data = sample_detection()
    data["before_image_id"] = before_id
    data["after_image_id"] = after_id

    response = client.post(
        "/api/v1/detections",
        json=data,
    )

    assert response.status_code == 201
    assert "id" in response.json()

    get_response = client.get(
        "/api/v1/detections"
    )

    assert get_response.status_code == 200
    assert len(get_response.json()) == 1


def test_invalid_confidence():
    register_two_images()

    data = sample_detection()
    data["confidence"] = 1.5

    response = client.post(
        "/api/v1/detections",
        json=data,
    )

    assert response.status_code == 422


def test_missing_image_reference():
    data = sample_detection()

    response = client.post(
        "/api/v1/detections",
        json=data,
    )

    assert response.status_code == 404


def test_same_before_and_after_image():
    register_two_images()

    data = sample_detection()
    data["after_image_id"] = data["before_image_id"]

    response = client.post(
        "/api/v1/detections",
        json=data,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "after_image_changes",
    [
        {"monitoring_area_id": 2},
        {"acquired_at": "2026-10-01T10:00:00Z"},
        {"crs": "EPSG:3857"},
    ],
)
def test_incompatible_image_pairs(after_image_changes):
    before_data = sample_image(
        "2026-11-01T10:00:00Z",
        "samples/before.tif",
    )

    after_data = sample_image(
        "2026-11-15T10:00:00Z",
        "samples/after.tif",
    )

    # Apply one incompatible condition.
    after_data.update(after_image_changes)

    before_response = client.post(
        "/api/v1/images",
        json=before_data,
    )

    after_response = client.post(
        "/api/v1/images",
        json=after_data,
    )

    assert before_response.status_code == 201
    assert after_response.status_code == 201

    detection = sample_detection()

    detection["before_image_id"] = before_response.json()["id"]
    detection["after_image_id"] = after_response.json()["id"]

    response = client.post(
        "/api/v1/detections",
        json=detection,
    )

    assert response.status_code == 422

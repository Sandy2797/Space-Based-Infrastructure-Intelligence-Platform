
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.api.detections import mock_detections


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_mock_detections():
    mock_detections.clear()
    yield
    mock_detections.clear()


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
    response = client.post(
        "/api/v1/detections",
        json=sample_detection(),
    )

    assert response.status_code == 201

    result = response.json()

    assert "id" in result
    assert result["origin_category"] == "human_made"
    assert result["confidence"] == 0.87

    get_response = client.get("/api/v1/detections")

    assert get_response.status_code == 200
    assert len(get_response.json()) == 1


def test_invalid_confidence():
    data = sample_detection()
    data["confidence"] = 1.5

    response = client.post(
        "/api/v1/detections",
        json=data,
    )

    assert response.status_code == 422

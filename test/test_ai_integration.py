from datetime import datetime, timezone

import pytest

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.services.ai_integration import (
    MockPointPrediction,
    prepare_detection_from_mock,
)


client = TestClient(app)


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


def test_mock_ai_prediction_can_be_registered():
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

    prediction = MockPointPrediction(
        longitude=31.2,
        latitude=30.2,
        origin_category="human_made",
        confidence=0.87,
    )

    detection = prepare_detection_from_mock(
        prediction,
        before_image_id=before.json()["id"],
        after_image_id=after.json()["id"],
        observed_at=datetime(
            2026, 11, 20, 10, 0,
            tzinfo=timezone.utc,
        ),
    )

    response = client.post(
        "/api/v1/detections",
        json=detection.model_dump(mode="json"),
    )

    assert response.status_code == 201

    saved = response.json()

    assert saved["origin_category"] == "human_made"
    assert saved["confidence"] == 0.87
    assert saved["geometry"]["coordinates"] == [
        31.2,
        30.2,
    ]

    # Verify that the detection can be retrieved.
    detections = client.get("/api/v1/detections")

    assert detections.status_code == 200
    assert len(detections.json()) == 1
    assert detections.json()[0]["id"] == saved["id"]


def test_mock_ai_rejects_invalid_confidence():
    with pytest.raises(ValidationError):
        MockPointPrediction(
            longitude=31.2,
            latitude=30.2,
            origin_category="human_made",
            confidence=1.5,
        )
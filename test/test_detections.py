
import pytest

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.models.detection import DetectionDB


client = TestClient(app)


def sample_image(
    acquired_at,
    file_reference,
    monitoring_area_id=1,
):
    return {
        "monitoring_area_id": monitoring_area_id,
        "provider": "synthetic_test_data",
        "file_reference": file_reference,
        "acquired_at": acquired_at,
        "crs": "EPSG:4326",
        "width": 1024,
        "height": 1024,
        "band_count": 3,
    }


def register_two_images(monitoring_area_id=1):

    before = client.post(
        "/api/v1/images",
        json=sample_image(
            "2026-11-01T10:00:00Z",
            "samples/before.tif",
            monitoring_area_id,
        ),
    )

    after = client.post(
        "/api/v1/images",
        json=sample_image(
            "2026-11-15T10:00:00Z",
            "samples/after.tif",
            monitoring_area_id,
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


def test_create_and_get_detection(two_monitoring_areas):

    before_id, after_id = register_two_images(
        two_monitoring_areas[0]
    )

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


def test_invalid_confidence(two_monitoring_areas):

    register_two_images(two_monitoring_areas[0])

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


def test_same_before_and_after_image(two_monitoring_areas):

    register_two_images(two_monitoring_areas[0])

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
def test_incompatible_image_pairs(
    after_image_changes,
    two_monitoring_areas,
):

    first_area_id, second_area_id = two_monitoring_areas

    before_data = sample_image(
        "2026-11-01T10:00:00Z",
        "samples/before.tif",
        first_area_id,
    )

    after_data = sample_image(
        "2026-11-15T10:00:00Z",
        "samples/after.tif",
        first_area_id,
    )

    changes = dict(after_image_changes)

    if "monitoring_area_id" in changes:
        changes["monitoring_area_id"] = second_area_id

    after_data.update(changes)

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


def test_detection_is_persisted_in_database(
    isolated_database,
    two_monitoring_areas,
):

    before_id, after_id = register_two_images(
        two_monitoring_areas[0]
    )

    detection = sample_detection()
    detection["before_image_id"] = before_id
    detection["after_image_id"] = after_id

    response = client.post(
        "/api/v1/detections",
        json=detection,
    )

    assert response.status_code == 201

    detection_id = response.json()["id"]

    with Session(isolated_database) as db:

        saved = db.get(
            DetectionDB,
            detection_id,
        )

        assert saved is not None
        assert saved.before_image_id == before_id
        assert saved.after_image_id == after_id
        assert saved.origin_category == "human_made"
        assert saved.confidence == 0.87
        assert saved.geometry["type"] == "Point"
        assert saved.geometry["coordinates"] == [
            31.2,
            30.2,
        ]


def create_detection_for_filters(
    monitoring_area_id,
    category="human_made",
    confidence=0.87,
    observed_at="2026-11-20T10:00:00Z",
):
    before_id, after_id = register_two_images(
        monitoring_area_id
    )

    data = sample_detection()
    data["before_image_id"] = before_id
    data["after_image_id"] = after_id
    data["origin_category"] = category
    data["confidence"] = confidence
    data["observed_at"] = observed_at

    response = client.post(
        "/api/v1/detections",
        json=data,
    )

    assert response.status_code == 201, response.text

    return response.json()


def test_filter_by_monitoring_area(two_monitoring_areas):
    first_area, second_area = two_monitoring_areas

    create_detection_for_filters(first_area)
    create_detection_for_filters(second_area, category="natural")

    response = client.get(
        "/api/v1/detections",
        params={"monitoring_area_id": first_area},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_by_category(two_monitoring_areas):
    area_id = two_monitoring_areas[0]

    create_detection_for_filters(area_id)
    create_detection_for_filters(
        area_id,
        category="natural",
    )

    response = client.get(
        "/api/v1/detections",
        params={"origin_category": "natural"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["origin_category"] == "natural"


def test_filter_by_confidence_range(two_monitoring_areas):
    area_id = two_monitoring_areas[0]

    create_detection_for_filters(area_id, confidence=0.4)
    create_detection_for_filters(area_id, confidence=0.75)
    create_detection_for_filters(area_id, confidence=0.95)

    response = client.get(
        "/api/v1/detections",
        params={
            "min_confidence": 0.7,
            "max_confidence": 0.8,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["confidence"] == 0.75


def test_filter_by_date_range(two_monitoring_areas):
    area_id = two_monitoring_areas[0]

    create_detection_for_filters(
        area_id,
        observed_at="2026-11-19T10:00:00Z",
    )

    create_detection_for_filters(
        area_id,
        observed_at="2026-11-20T10:00:00Z",
    )

    create_detection_for_filters(
        area_id,
        observed_at="2026-11-21T10:00:00Z",
    )

    response = client.get(
        "/api/v1/detections",
        params={
            "start_date": "2026-11-20",
            "end_date": "2026-11-20",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_reject_invalid_confidence_range():
    response = client.get(
        "/api/v1/detections",
        params={
            "min_confidence": 0.9,
            "max_confidence": 0.2,
        },
    )

    assert response.status_code == 422


def test_reject_invalid_date_range():
    response = client.get(
        "/api/v1/detections",
        params={
            "start_date": "2026-11-25",
            "end_date": "2026-11-20",
        },
    )

    assert response.status_code == 422

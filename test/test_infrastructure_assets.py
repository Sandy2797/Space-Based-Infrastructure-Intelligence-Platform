
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def sample_area():
    return {
        "name": "Test Monitoring Area",
        "crs": "EPSG:4326",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [31.0, 30.0],
                [31.1, 30.0],
                [31.1, 30.1],
                [31.0, 30.1],
                [31.0, 30.0],
            ]],
        },
    }


def create_monitoring_area():
    response = client.post(
        "/api/v1/monitoring-areas",
        json=sample_area(),
    )

    assert response.status_code == 201

    return response.json()["id"]


def sample_asset(monitoring_area_id, location=None):
    if location is None:
        location = {
            "type": "Point",
            "coordinates": [31.05, 30.05],
        }

    return {
        "monitoring_area_id": monitoring_area_id,
        "asset_name": "Test Building",
        "asset_type": "building",
        "location": location,
    }


def test_create_infrastructure_asset():
    area_id = create_monitoring_area()

    response = client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(area_id),
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["asset_name"] == "Test Building"
    assert response.json()["monitoring_area_id"] == area_id


def test_list_infrastructure_assets():
    area_id = create_monitoring_area()

    client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(area_id),
    )

    response = client.get(
        "/api/v1/infrastructure-assets"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_infrastructure_asset():
    area_id = create_monitoring_area()

    create_response = client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(area_id),
    )

    asset_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/infrastructure-assets/{asset_id}"
    )

    assert response.status_code == 200
    assert response.json()["asset_name"] == "Test Building"


def test_get_missing_infrastructure_asset():
    response = client.get(
        "/api/v1/infrastructure-assets/999"
    )

    assert response.status_code == 404


def test_reject_missing_monitoring_area():
    response = client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(999),
    )

    assert response.status_code == 404


def test_reject_asset_outside_monitoring_area():
    area_id = create_monitoring_area()

    location = {
        "type": "Point",
        "coordinates": [31.2, 30.2],
    }

    response = client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(area_id, location),
    )

    assert response.status_code == 422


def test_reject_invalid_coordinate_ranges():
    area_id = create_monitoring_area()

    location = {
        "type": "Point",
        "coordinates": [181, 30],
    }

    response = client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(area_id, location),
    )

    assert response.status_code == 422


def test_reject_unsupported_geometry():
    area_id = create_monitoring_area()

    location = {
        "type": "GeometryCollection",
        "geometries": [],
    }

    response = client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(area_id, location),
    )

    assert response.status_code == 422


def test_reject_invalid_polygon():
    area_id = create_monitoring_area()

    location = {
        "type": "Polygon",
        "coordinates": [[
            [31.02, 30.02],
            [31.08, 30.08],
            [31.08, 30.02],
            [31.02, 30.08],
            [31.02, 30.02],
        ]],
    }

    response = client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(area_id, location),
    )

    assert response.status_code == 422


def test_reject_empty_asset_name():
    area_id = create_monitoring_area()

    data = sample_asset(area_id)
    data["asset_name"] = "   "

    response = client.post(
        "/api/v1/infrastructure-assets",
        json=data,
    )

    assert response.status_code == 422


def test_create_road_using_linestring():
    area_id = create_monitoring_area()

    location = {
        "type": "LineString",
        "coordinates": [
            [31.02, 30.02],
            [31.05, 30.05],
            [31.08, 30.08],
        ],
    }

    data = sample_asset(area_id, location)
    data["asset_name"] = "Test Road"
    data["asset_type"] = "road"

    response = client.post(
        "/api/v1/infrastructure-assets",
        json=data,
    )

    assert response.status_code == 201
    assert response.json()["asset_type"] == "road"

def test_filter_assets_by_monitoring_area():
    first_area = create_monitoring_area()
    second_area = create_monitoring_area()

    client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(first_area),
    )

    client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(second_area),
    )

    response = client.get(
        f"/api/v1/infrastructure-assets?monitoring_area_id={first_area}"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["monitoring_area_id"] == first_area


def test_filter_assets_by_type():
    area_id = create_monitoring_area()

    client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(area_id),
    )

    road = sample_asset(area_id)
    road["asset_name"] = "Test Road"
    road["asset_type"] = "road"

    client.post(
        "/api/v1/infrastructure-assets",
        json=road,
    )

    response = client.get(
        "/api/v1/infrastructure-assets?asset_type=ROAD"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["asset_type"] == "road"


def test_filter_assets_by_bounding_box():
    area_id = create_monitoring_area()

    client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(area_id),
    )

    second_location = {
        "type": "Point",
        "coordinates": [31.08, 30.08],
    }

    client.post(
        "/api/v1/infrastructure-assets",
        json=sample_asset(area_id, second_location),
    )

    response = client.get(
        "/api/v1/infrastructure-assets",
        params={
            "bbox": "31.04,30.04,31.06,30.06"
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["asset_name"] == "Test Building"


def test_reject_malformed_bounding_box():
    response = client.get(
        "/api/v1/infrastructure-assets?bbox=31,30,31.1"
    )

    assert response.status_code == 422


def test_reject_invalid_bounding_box_coordinates():
    response = client.get(
        "/api/v1/infrastructure-assets",
        params={
            "bbox": "31.1,30,31.0,30.1"
        },
    )

    assert response.status_code == 422

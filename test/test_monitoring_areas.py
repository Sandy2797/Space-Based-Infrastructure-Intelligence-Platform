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


def test_create_monitoring_area():
    response = client.post(
        "/api/v1/monitoring-areas",
        json=sample_area(),
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Test Monitoring Area"


def test_list_monitoring_areas():
    client.post(
        "/api/v1/monitoring-areas",
        json=sample_area(),
    )

    response = client.get(
        "/api/v1/monitoring-areas"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_missing_monitoring_area():
    response = client.get(
        "/api/v1/monitoring-areas/999"
    )

    assert response.status_code == 404


def test_reject_point_as_monitoring_area():
    area = sample_area()

    area["geometry"] = {
        "type": "Point",
        "coordinates": [31.2, 30.2],
    }

    response = client.post(
        "/api/v1/monitoring-areas",
        json=area,
    )

    assert response.status_code == 422


def test_reject_invalid_polygon():
    area = sample_area()

    # Self-intersecting polygon.
    area["geometry"]["coordinates"] = [[
        [31.0, 30.0],
        [31.1, 30.1],
        [31.1, 30.0],
        [31.0, 30.1],
        [31.0, 30.0],
    ]]

    response = client.post(
        "/api/v1/monitoring-areas",
        json=area,
    )

    assert response.status_code == 422


def test_create_monitoring_area_transforms_epsg3857():
    area = sample_area()

    area["crs"] = "EPSG:3857"

    area["geometry"] = {
        "type": "Polygon",
        "coordinates": [[
            [3449000, 3499000],
            [3451000, 3499000],
            [3451000, 3501000],
            [3449000, 3501000],
            [3449000, 3499000],
        ]],
    }

    response = client.post(
        "/api/v1/monitoring-areas",
        json=area,
    )

    assert response.status_code == 201, response.text

    result = response.json()

    assert result["crs"] == "EPSG:3857"
    assert result["geometry_crs"] == "EPSG:4326"

    coordinates = result["geometry"]["coordinates"][0]

    # Coordinates must now be longitude and latitude.
    for longitude, latitude in coordinates:
        assert -180 <= longitude <= 180
        assert -90 <= latitude <= 90

    # They must not still contain projected coordinates.
    assert coordinates[0] != [3449000, 3499000]
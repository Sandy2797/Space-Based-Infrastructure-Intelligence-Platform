
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.main import app
from app.db.database import engine
from app.models.monitoring_area import MonitoringAreaDB
from app.models.infrastructure_asset import InfrastructureAssetDB
from app.models.satellite_image import SatelliteImageDB
from app.models.detection import DetectionDB


def main():
    if engine.dialect.name != "postgresql":
        raise RuntimeError(
            "This integration check must use PostgreSQL. "
            f"Current database: {engine.dialect.name}"
        )

    marker = uuid4().hex[:12]
    area_name = f"PostGIS Integration {marker}"

    client = TestClient(app)
    client.__enter__()
    area_id = None

    print("Connected database:", engine.dialect.name)
    print("Starting PostGIS integration check...")

    try:
        # 1. Create a monitoring area.
        area_response = client.post(
            "/api/v1/monitoring-areas",
            json={
                "name": area_name,
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
            },
        )
        assert area_response.status_code == 201, area_response.text
        area_id = area_response.json()["id"]
        print("[PASS] Monitoring area created:", area_id)

        # 2. Register before and after satellite images.
        image_ids = []

        for date, suffix in [
            ("2026-11-01T10:00:00Z", "before"),
            ("2026-11-15T10:00:00Z", "after"),
        ]:
            image_response = client.post(
                "/api/v1/images",
                json={
                    "monitoring_area_id": area_id,
                    "provider": "integration_test",
                    "file_reference": f"integration/{marker}/{suffix}.tif",
                    "acquired_at": date,
                    "crs": "EPSG:4326",
                    "width": 1024,
                    "height": 1024,
                    "band_count": 3,
                },
            )
            assert image_response.status_code == 201, image_response.text
            image_ids.append(image_response.json()["id"])

        before_id, after_id = image_ids
        print("[PASS] Both satellite images registered:", image_ids)

        # 3. Create an infrastructure asset inside the area.
        asset_response = client.post(
            "/api/v1/infrastructure-assets",
            json={
                "monitoring_area_id": area_id,
                "asset_name": f"Integration Building {marker}",
                "asset_type": "building",
                "location": {
                    "type": "Point",
                    "coordinates": [31.05, 30.05],
                },
            },
        )
        assert asset_response.status_code == 201, asset_response.text
        asset_id = asset_response.json()["id"]
        print("[PASS] Infrastructure asset created:", asset_id)

        # 4. Create a detection linked to both images.
        detection_response = client.post(
            "/api/v1/detections",
            json={
                "before_image_id": before_id,
                "after_image_id": after_id,
                "observed_at": "2026-11-20T10:00:00Z",
                "geometry": {
                    "type": "Point",
                    "coordinates": [31.0505, 30.05],
                },
                "origin_category": "human_made",
                "confidence": 0.87,
                "model_version": "integration-test-v1",
            },
        )
        assert detection_response.status_code == 201, detection_response.text
        detection_id = detection_response.json()["id"]
        print("[PASS] Detection created:", detection_id)

        # 5. Find detections within 500 metres of the asset.
        nearby_response = client.get(
            f"/api/v1/detections/near-asset/{asset_id}",
            params={"radius_m": 500},
        )
        assert nearby_response.status_code == 200, nearby_response.text

        nearby_detections = nearby_response.json()
        assert any(
            item["id"] == detection_id
            for item in nearby_detections
        ), "Created detection was not returned by the nearby query."

        print("[PASS] PostGIS nearby-detection query returned the detection.")
        print("\nALL POSTGIS INTEGRATION CHECKS PASSED.")

    finally:
        # Remove only records belonging to this test's monitoring area.
        if area_id is not None:
            with Session(engine) as db:
                area_image_ids = select(SatelliteImageDB.id).where(
                    SatelliteImageDB.monitoring_area_id == area_id
                )

                db.execute(
                    delete(DetectionDB).where(
                        or_(
                            DetectionDB.before_image_id.in_(area_image_ids),
                            DetectionDB.after_image_id.in_(area_image_ids),
                        )
                    )
                )

                db.execute(
                    delete(InfrastructureAssetDB).where(
                        InfrastructureAssetDB.monitoring_area_id == area_id
                    )
                )

                db.execute(
                    delete(SatelliteImageDB).where(
                        SatelliteImageDB.monitoring_area_id == area_id
                    )
                )

                db.execute(
                    delete(MonitoringAreaDB).where(
                        MonitoringAreaDB.id == area_id
                    )
                )

                db.commit()

            print("Integration-test records cleaned up.")
            client.__exit__(None, None, None)

if __name__ == "__main__":
    main()
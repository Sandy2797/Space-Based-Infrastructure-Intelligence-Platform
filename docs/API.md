# Backend API Reference

**API version:** 0.1.0  
**Base URL:** `http://127.0.0.1:8000`  
**API prefix:** `/api/v1`

Interactive documentation: `/docs`  
OpenAPI document: `/openapi.json`

## 1. General endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Project status |
| GET | `/health` | Basic application health response |

## 2. Monitoring areas

Base path: `/api/v1/monitoring-areas`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/` | Create a monitoring area |
| GET | `/` | List monitoring areas |
| GET | `/{area_id}` | Retrieve one monitoring area |

Create request:

```json
{
  "name": "Cairo Monitoring Zone",
  "crs": "EPSG:4326",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[31.0, 30.0], [31.1, 30.0], [31.1, 30.1], [31.0, 30.1], [31.0, 30.0]]]
  }
}
```

The geometry must be a valid, non-empty Polygon or MultiPolygon. Input geometry is transformed to the backend storage CRS, EPSG:4326. GeoJSON coordinate order is longitude, latitude.

## 3. Infrastructure assets

Base path: `/api/v1/infrastructure-assets`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/` | Register an asset |
| GET | `/` | List assets; supports `monitoring_area_id`, `asset_type`, and `bbox` filters |
| GET | `/{asset_id}` | Retrieve one asset |

Create request:

```json
{
  "monitoring_area_id": 1,
  "asset_name": "Main Building",
  "asset_type": "building",
  "crs": "EPSG:4326",
  "location": {"type": "Point", "coordinates": [31.05, 30.05]}
}
```

Supported geometry types: Point, MultiPoint, LineString, MultiLineString, Polygon, and MultiPolygon. Geometry is validated, transformed to EPSG:4326, and must be completely covered by the selected monitoring area. The request CRS is used for transformation; the current asset model stores the normalized geometry, not a separate original-source-CRS field.

The `bbox` query format is `west,south,east,north` in EPSG:4326. Bounds must be finite and geographically valid.

## 4. Satellite images

Base path: `/api/v1/images`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/` | Register image metadata |
| GET | `/` | List registered images |
| GET | `/{image_id}` | Retrieve one image |

Create request:

```json
{
  "monitoring_area_id": 1,
  "provider": "synthetic_test_data",
  "file_reference": "samples/image_before.tif",
  "acquired_at": "2026-11-01T10:00:00Z",
  "crs": "EPSG:4326",
  "width": 1024,
  "height": 1024,
  "band_count": 3
}
```

The monitoring area must exist. Provider, file reference, and CRS must be non-empty. Acquisition time must be timezone-aware and is normalized to UTC. Width, height, and band count must be positive.

**Important:** This endpoint registers metadata and a file reference. It does not upload a raster. Rasterio metadata extraction is available through the backend service `prepare_image_registration(file_path, monitoring_area_id, provider, acquired_at)`; callers must supply a locally accessible raster path to that service.

## 5. Detections

Base path: `/api/v1/detections`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/` | Validate and persist a detection |
| GET | `/` | List detections with filters |
| GET | `/near-asset/{asset_id}` | Find detections within a radius of an asset |

Current create request shape:

```json
{
  "before_image_id": 1,
  "after_image_id": 2,
  "observed_at": "2026-11-20T10:00:00Z",
  "geometry": {"type": "Polygon", "coordinates": [[[31.02, 30.02], [31.03, 30.02], [31.03, 30.03], [31.02, 30.03], [31.02, 30.02]]]},
  "component_id": 8,
  "origin_category": "uncertain",
  "confidence": null,
  "change_score": 0.82,
  "threshold": {"value": 0.4},
  "pixel_count": 120,
  "area_m2": 12000,
  "evidence_quality": {"image_quality": "acceptable", "alignment": "checked"},
  "quality_flags": [],
  "mask_reference": "approved-storage-reference",
  "model_version": "image-differencing-baseline-v1.0.0"
}
```

Geometry supports Point, Polygon, and MultiPolygon. The before and after image IDs must be different, exist, belong to the same monitoring area, have chronologically ordered acquisition times, and have matching CRS strings. `observed_at` must include timezone information. Detection geometry is transformed to EPSG:4326 and must be covered by the monitoring-area geometry.

The category is `human_made`, `natural`, or `uncertain`. Confidence is optional and, when supplied, must be between 0 and 1. The API retains optional component, change-score, threshold, pixel-count, area, evidence-quality, quality-flag, and mask-reference metadata. Model version is required.

List filters:
- `monitoring_area_id`
- `origin_category`
- `min_confidence` and `max_confidence` (each from 0 to 1; minimum cannot exceed maximum)
- `start_date` and `end_date` (UTC calendar dates; both endpoints inclusive)

Nearby query:
`GET /api/v1/detections/near-asset/1?radius_m=500`

The radius must be greater than zero and at most 100,000 metres. PostgreSQL uses PostGIS geography distance; SQLite tests use a local metric projection. Results are restricted to the asset's monitoring area.

## 6. Responses and errors

| Status | Meaning |
|---|---|
| 200 | Successful retrieval |
| 201 | Resource created |
| 404 | Requested resource or referenced record does not exist |
| 422 | Request validation or business-rule validation failed |

FastAPI/Pydantic request validation errors also return 422.

## 7. Spatial and evidence conventions

- Geometry storage CRS: EPSG:4326.
- GeoJSON positions use longitude, latitude.
- PostgreSQL uses PostGIS geometry; SQLite uses JSON geometry for tests/development.
- Original raster files are not modified by metadata extraction.
- A missing confidence value remains null; it must not be replaced with an invented score.
- A missing permit record must not be interpreted as proof of illegal activity.
- Predictions and recommendations are decision support and require authorized human review.

## 8. Current limitations

- Update and delete endpoints are not implemented.
- Image metadata registration is separate from raster upload and production object storage.
- Authentication/authorization, permit records, NBVE verification cases, dashboard integration, feedback, and audit integration depend on the relevant team contracts.
- Pagination is not currently implemented on collection endpoints.

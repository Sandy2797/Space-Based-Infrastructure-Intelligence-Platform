# Space-Based Infrastructure Intelligence Platform
## Backend API Reference

**API version:** 0.1.0
**Base URL:** `http://localhost:8000`
**API prefix:** `/api/v1`

Interactive API documentation is available at `/docs` when the FastAPI application is running. The OpenAPI schema is available at `/openapi.json`.

---

## 1. General endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns project information and running status |
| GET | `/health` | Checks backend health |

### GET `/`

Example response:

```json
{
  "project": "Space-Based Infrastructure Intelligence Platform",
  "status": "running"
}
```

### GET `/health`

Example response:

```json
{
  "status": "healthy",
  "service": "backend"
}
```

---

## 2. Monitoring Areas

Base path: `/api/v1/monitoring-areas`

### POST `/api/v1/monitoring-areas`

Creates a monitoring area.

Request body:

```json
{
  "name": "Cairo Monitoring Zone",
  "crs": "EPSG:4326",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[
      [31.0, 30.0],
      [31.1, 30.0],
      [31.1, 30.1],
      [31.0, 30.1],
      [31.0, 30.0]
    ]]
  }
}
```

Requirements:
- Name must contain 1–120 characters.
- Geometry must be a valid, non-empty Polygon or MultiPolygon.
- CRS defaults to `EPSG:4326`.
- Input geometry is transformed into the backend storage CRS, `EPSG:4326`.

Success: `201 Created`

Example response:

```json
{
  "id": 1,
  "name": "Cairo Monitoring Zone",
  "crs": "EPSG:4326",
  "geometry_crs": "EPSG:4326",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[
      [31.0, 30.0],
      [31.1, 30.0],
      [31.1, 30.1],
      [31.0, 30.1],
      [31.0, 30.0]
    ]]
  }
}
```

### GET `/api/v1/monitoring-areas`

Returns all monitoring areas, ordered by ID.

Success: `200 OK`

### GET `/api/v1/monitoring-areas/{area_id}`

Returns one monitoring area.

Possible errors:
- `404 Not Found` — monitoring area does not exist.

---

## 3. Infrastructure Assets

Base path: `/api/v1/infrastructure-assets`

### POST `/api/v1/infrastructure-assets`

Registers an infrastructure asset inside a monitoring area.

Request body:

```json
{
  "monitoring_area_id": 1,
  "asset_name": "Main Building",
  "asset_type": "building",
  "crs": "EPSG:4326",
  "location": {
    "type": "Point",
    "coordinates": [31.05, 30.05]
  }
}
```

Requirements:
- `monitoring_area_id` must be positive and refer to an existing monitoring area.
- `asset_name` must contain 1–120 characters.
- `asset_type` must contain 1–80 characters.
- CRS defaults to `EPSG:4326`.
- Supported geometry types: Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon.
- Geometry must be valid, non-empty, and contain finite coordinates.
- The transformed asset geometry must be covered by its monitoring area.

Success: `201 Created`

Example response:

```json
{
  "id": 1,
  "monitoring_area_id": 1,
  "asset_name": "Main Building",
  "asset_type": "building",
  "location": {
    "type": "Point",
    "coordinates": [31.05, 30.05]
  },
  "location_crs": "EPSG:4326"
}
```

Possible errors:
- `404 Not Found` — monitoring area does not exist.
- `422 Unprocessable Entity` — invalid geometry, CRS, or asset outside its monitoring area.

### GET `/api/v1/infrastructure-assets`

Returns infrastructure assets with optional filters.

Query parameters:

| Parameter | Type | Description |
|---|---|---|
| `monitoring_area_id` | Integer | Filter by monitoring area |
| `asset_type` | String | Filter by asset type, case-insensitive |
| `bbox` | String | Geographic bounding box: `west,south,east,north` |

Example:

```http
GET /api/v1/infrastructure-assets?monitoring_area_id=1&asset_type=building&bbox=31.0,30.0,31.1,30.1
```

Bounding-box requirements:
- Exactly four finite coordinates.
- Longitude range: -180 to 180.
- Latitude range: -90 to 90.
- West must be less than east.
- South must be less than north.

Success: `200 OK`

### GET `/api/v1/infrastructure-assets/{asset_id}`

Returns one infrastructure asset.

Possible errors:
- `404 Not Found` — infrastructure asset does not exist.

---

## 4. Satellite Images

Base path: `/api/v1/images`

### POST `/api/v1/images`

Registers satellite image metadata.

Request body:

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

Requirements:
- `monitoring_area_id` must be positive. The database enforces its relationship with the monitoring area.
- Provider, file reference, and CRS must not be empty.
- Acquisition timestamp must include timezone information.
- Width, height, and band count must be positive integers.
- Acquisition timestamps are normalized to UTC before storage.

Success: `201 Created`

Example response:

```json
{
  "id": 1,
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

### GET `/api/v1/images`

Returns all registered satellite images, ordered by ID.

Success: `200 OK`

### GET `/api/v1/images/{image_id}`

Returns one satellite image.

Possible errors:
- `404 Not Found` — satellite image does not exist.

---

## 5. Detections

Base path: `/api/v1/detections`

### POST `/api/v1/detections`

Creates and persists a detection.

Request body:

```json
{
  "before_image_id": 1,
  "after_image_id": 2,
  "observed_at": "2026-11-20T10:00:00Z",
  "geometry": {
    "type": "Point",
    "coordinates": [31.2, 30.2]
  },
  "origin_category": "human_made",
  "confidence": 0.87,
  "model_version": "mock-v0"
}
```

Requirements:
- Before and after image IDs must refer to existing images.
- The two images must be different.
- Both images must belong to the same monitoring area.
- The before-image acquisition time must be earlier than the after-image acquisition time.
- Both images must have the same CRS string.
- `observed_at` must include timezone information.
- Detection geometry must be a GeoJSON Point with exactly two coordinates.
- `origin_category` must be `human_made`, `natural`, or `uncertain`.
- Confidence must be between 0 and 1.
- Model version must not be empty.

Success: `201 Created`

Example response:

```json
{
  "id": "generated-detection-uuid",
  "before_image_id": 1,
  "after_image_id": 2,
  "observed_at": "2026-11-20T10:00:00Z",
  "geometry": {
    "type": "Point",
    "coordinates": [31.2, 30.2]
  },
  "origin_category": "human_made",
  "confidence": 0.87,
  "model_version": "mock-v0"
}
```

Possible errors:
- `404 Not Found` — before-image or after-image does not exist.
- `422 Unprocessable Entity` — invalid image pair, timestamp, geometry, category, or confidence.

### GET `/api/v1/detections`

Returns detections with optional filters.

Query parameters:

| Parameter | Type | Description |
|---|---|---|
| `monitoring_area_id` | Integer | Filter by monitoring area |
| `origin_category` | String | `human_made`, `natural`, or `uncertain` |
| `min_confidence` | Float | Minimum confidence, from 0 to 1 |
| `max_confidence` | Float | Maximum confidence, from 0 to 1 |
| `start_date` | Date | Inclusive start date, interpreted as UTC |
| `end_date` | Date | Inclusive end date, interpreted as UTC |

Example:

```http
GET /api/v1/detections?monitoring_area_id=1&origin_category=human_made&min_confidence=0.7&max_confidence=1&start_date=2026-11-01&end_date=2026-11-30
```

The minimum confidence cannot exceed the maximum confidence. The start date cannot be after the end date.

Success: `200 OK`

### GET `/api/v1/detections/near-asset/{asset_id}`

Returns detections within a specified distance of an infrastructure asset, restricted to the asset's monitoring area.

Query parameter:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `radius_m` | Float | 500 | Search radius in metres; must be greater than 0 and no more than 100,000 |

Example:

```http
GET /api/v1/detections/near-asset/1?radius_m=500
```

PostgreSQL uses PostGIS `ST_DWithin` with geography casts for metre-based distance calculations. SQLite uses a local metric projection for test calculations.

Possible errors:
- `404 Not Found` — infrastructure asset does not exist.
- `422 Unprocessable Entity` — invalid radius.

Success: `200 OK`

---

## 6. Spatial and CRS conventions

- Backend geometry storage CRS: `EPSG:4326`.
- GeoJSON coordinates use longitude, latitude order.
- Monitoring area geometry is Polygon or MultiPolygon.
- Detection geometry is Point.
- Infrastructure asset geometry accepts the supported GeoJSON geometry types documented above.
- Monitoring area and infrastructure asset creation accept an input CRS and transform geometry into the storage CRS.
- Monitoring area responses include `geometry_crs`.
- Infrastructure asset responses include `location_crs`.
- Detection responses return stored geometry in the backend storage CRS.

---

## 7. General response and error conventions

| Status | Meaning |
|---|---|
| `200 OK` | Successful retrieval |
| `201 Created` | Resource created |
| `404 Not Found` | Requested resource or referenced record not found |
| `422 Unprocessable Entity` | Invalid request data or failed business validation |

FastAPI/Pydantic request validation errors also use `422`.

---

## 8. Current API limitations

The current backend exposes creation and retrieval operations for these resources. Update and delete endpoints are not currently implemented.

Satellite image registration stores metadata and a file reference; it does not itself upload or process the referenced raster file.

Detection creation currently accepts a Point geometry and the existing detection fields. Additional AI evidence, uncertainty, and forecasting fields should be added only after the team agrees on the corresponding integration contract.

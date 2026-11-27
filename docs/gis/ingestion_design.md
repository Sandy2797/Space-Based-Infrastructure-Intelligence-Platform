# GIS Ingestion and Processing Design

## 1. Purpose
This document describes the current Backend and GIS ingestion responsibilities and the boundary between implemented processing and future integrations.

## 2. Satellite Image Registration
The current image registration API is:

`POST /api/v1/images`

It stores:
- Monitoring area identifier.
- Provider.
- File reference.
- Acquisition timestamp.
- Source CRS metadata.
- Raster width.
- Raster height.
- Band count.

The acquisition timestamp must be timezone-aware and is normalized to UTC.

Raster metadata extraction is integrated with registration. The endpoint stores metadata and a file reference; it does not upload the raster file or execute the AI model.

## 3. Monitoring Areas
The monitoring area API accepts Polygon or MultiPolygon GeoJSON.

Input geometry is validated and transformed into EPSG:4326 before storage.

Endpoints:
- `POST /api/v1/monitoring-areas`
- `GET /api/v1/monitoring-areas`
- `GET /api/v1/monitoring-areas/{area_id}`

## 4. Infrastructure Assets
The infrastructure asset API supports:
- Point.
- MultiPoint.
- LineString.
- MultiLineString.
- Polygon.
- MultiPolygon.

Incoming geometries are validated and transformed into EPSG:4326. The complete asset geometry must be covered by its associated monitoring area.

Endpoints:
- `POST /api/v1/infrastructure-assets`
- `GET /api/v1/infrastructure-assets`
- `GET /api/v1/infrastructure-assets/{asset_id}`

The collection endpoint supports monitoring area, asset type, and bounding-box filters.

## 5. Detection Geometry
The current detection API accepts GeoJSON Point geometry with longitude and latitude coordinates.

Detection records reference before and after satellite images. The backend validates that:
- Both images exist.
- The image identifiers differ.
- Both images belong to the same monitoring area.
- The before image was acquired earlier.
- Both image CRS metadata values match.
- The observation timestamp is timezone-aware.
- Confidence is between 0 and 1.

The current detection schema must not be assumed to support polygon masks. Any change to support AI-generated Polygon or MultiPolygon outputs requires agreement with the AI component owner and a corresponding database/API design review.

## 6. Spatial Storage
PostgreSQL uses PostGIS geometry columns with SRID 4326.

Current geometry columns:
- `monitoring_areas.geometry`: GEOMETRY.
- `infrastructure_assets.location`: GEOMETRY.
- `detections.geometry`: POINT.

SQLite uses JSON geometry storage for local development and automated tests.

GiST spatial indexes are implemented for the three PostgreSQL geometry columns.

## 7. Spatial Queries
The backend provides a nearby-detection endpoint:

`GET /api/v1/detections/near-asset/{asset_id}?radius_m=500`

PostgreSQL uses PostGIS `ST_DWithin` with geography-based distance calculations. SQLite uses a local metric projection for test calculations.

The endpoint restricts results to the infrastructure asset's monitoring area.

## 8. File Integrity and Storage
Original satellite imagery must remain unchanged.

The database stores metadata and file references rather than raster bytes in ordinary database rows. The final production file/object storage provider and access mechanism remain to be confirmed.

## 9. Current Processing Boundaries
**Implemented:**
- Image metadata registration.
- Raster metadata extraction.
- Geometry validation.
- CRS transformation.
- Monitoring area and infrastructure asset persistence.
- Detection persistence and retrieval.
- PostGIS spatial queries.

**Pending:**
- Production raster/object storage.
- AI inference and evidence-quality integration.
- Final AI geometry and detection contract.
- Forecast integration.
- Permit data integration.
- NBVE integration.

## 10. Integration Requirements
Before changing the detection schema, agree on:
- Geometry type and CRS.
- Detection JSON structure.
- Model version.
- Confidence and uncertainty semantics.
- Evidence-quality fields.
- Mask or raster reference requirements.
- Forecast fields and timestamps.

See `docs/API.md` for current API contracts.

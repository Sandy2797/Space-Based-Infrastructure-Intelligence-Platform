# Technical Decisions Document

## Project
Space-Based Infrastructure Intelligence Platform

## 1. Purpose
This document records the Backend and GIS technical decisions, their rationale, implementation status, and remaining integration dependencies.

## 2. Backend Framework
**Decision:** Python with FastAPI.

**Reason:**
- FastAPI supports versioned REST API development.
- Pydantic provides request and response validation.
- OpenAPI provides interactive API documentation.
- Python supports established geospatial libraries.

**Status:** Implemented.

## 3. Database and ORM
**Decision:** SQLAlchemy with PostgreSQL/PostGIS as the primary spatial database and SQLite as a supported development and testing option.

**Reason:**
- SQLAlchemy provides database models and session management.
- PostgreSQL provides persistent relational storage.
- PostGIS provides native geometry storage and spatial operations.
- SQLite supports isolated automated tests.

**Status:**
- SQLAlchemy: Implemented.
- PostgreSQL: Implemented and tested locally.
- PostGIS: Implemented and tested locally.
- SQLite fallback and test configuration: Implemented.
- Production deployment: Pending.

## 4. Geospatial Processing
**Selected technologies:**
- Rasterio: Raster metadata extraction.
- Shapely: Geometry validation and spatial operations.
- GeoPandas: Geospatial data manipulation.
- PyProj: CRS handling and coordinate transformations.
- GeoAlchemy2: SQLAlchemy integration with PostGIS geometry.

**Status:** The libraries required by the current backend GIS implementation are integrated. Further raster processing and AI pipeline integration remain pending.

## 5. Coordinate Reference Systems
**Decision:** Use EPSG:4326 as the backend geometry storage CRS.

**Conventions:**
- GeoJSON coordinates use longitude, latitude order.
- Monitoring area and infrastructure asset input geometries are transformed to EPSG:4326.
- Satellite images retain their source CRS metadata.
- Detection creation currently requires matching CRS metadata for the before and after images.
- Detection geometry is currently stored and returned in the backend storage CRS.

**Status:** CRS normalization and geometry transformation are implemented. The final detection geometry contract with the AI component requires confirmation.

## 6. Geographic Geometry Storage
**Decision:** Use native PostGIS geometry columns in PostgreSQL and JSON geometry storage in SQLite.

**Current geometry types:**
- Monitoring areas: GEOMETRY, SRID 4326.
- Infrastructure assets: GEOMETRY, SRID 4326.
- Detections: POINT, SRID 4326.

**Status:**
- PostGIS geometry storage: Implemented.
- SQLite JSON geometry storage: Implemented.
- GiST spatial indexes: Implemented.
- Nearby detection spatial query: Implemented and tested locally.

## 7. Satellite Image File Management
**Decision:** Store image metadata and file references in the relational database rather than storing large raster files directly in database rows.

**Rules:**
- Original satellite imagery must remain unchanged.
- File references identify approved source imagery.
- Raster metadata extraction is integrated with image registration.
- Actual raster upload and production file/object storage are separate concerns.

**Status:** Metadata registration, metadata extraction, and file references are implemented. Production file/object storage remains to be confirmed.

## 8. API Architecture
**Decision:** Use versioned REST APIs with JSON request and response formats.

**Current API prefix:** `/api/v1/`

**Implemented resources:**
- Monitoring areas: creation and retrieval.
- Infrastructure assets: registration, retrieval, and filtering.
- Satellite images: metadata registration and retrieval.
- Detections: creation, retrieval, filtering, and nearby-asset spatial queries.

**Pending resources and integrations:**
- Permit records.
- Verification cases.
- Dashboard-specific integration.
- Feedback and audit integration.

**Status:** Initial Backend and GIS API implementation is complete for the resources listed above. Team integration contracts remain pending.

## 9. Data Validation and Integrity
**Decision:** Apply validation at API and database levels where appropriate.

**Technologies:**
- Pydantic: API validation.
- Shapely: geometry validation and spatial relationships.
- SQLAlchemy: database operations.
- PostgreSQL constraints and foreign keys: persistent data integrity.

**Implemented rules include:**
- Positive image dimensions and band counts.
- Valid monitoring area geometries.
- CRS normalization and geometry transformation.
- Infrastructure asset containment within its monitoring area.
- Satellite image and monitoring area foreign-key relationships.
- Detection references to existing before and after images.
- Different before and after images belonging to the same monitoring area.
- Chronological image acquisition validation.
- Confidence values between 0 and 1.
- Valid detection origin categories.

**Status:** The listed initial validation and database relationships are implemented. Additional constraints may be required after team contracts are agreed.

## 10. Timestamp Standards
**Decision:** Require timezone-aware timestamps and normalize stored timestamps to UTC.

**Status:**
- Satellite image acquisition timestamp validation and UTC normalization: Implemented.
- Detection observation timestamp validation and UTC normalization: Implemented.

## 11. Evidence Integrity and Security
**Rules:**
- Original satellite imagery must remain unchanged.
- Restricted information must not be committed to GitHub.
- Permit records require authorized access.
- Detection confidence and model version must be retained.
- Important system actions should be auditable.
- Verification recommendations must remain subject to human review.

**Status:** Evidence-handling constraints are documented. Full authentication, authorization, and audit integration remain dependent on the relevant team components.

## 12. Team Integration Strategy
Use documented API contracts between independently developed components.

**Dependencies:**
- Nada: AI detection output, geometry, confidence, evidence quality, and forecasting fields.
- Rana: NBVE input/output contract and verification-case requirements.
- Seif: Authentication, authorization, and restricted-data requirements.
- Mohamed: Feedback and audit event requirements.
- Sandy: Backend APIs, GIS processing, database persistence, and integration.

Temporary mock data may be used for independent backend testing until actual component contracts are agreed.

**Status:** Initial backend APIs and database infrastructure are implemented. Final integration contracts remain pending.

## 13. Human-in-the-Loop Decision Making
The platform provides decision support, not autonomous legal or enforcement decisions.

A missing permit record does not establish illegal activity. AI predictions and verification recommendations must remain subject to authorized human review.

**Status:** Adopted as a project design constraint.

## 14. Pending Technical Decisions
1. Production PostgreSQL/PostGIS deployment configuration.
2. Production satellite raster file/object storage.
3. Final detection geometry and AI evidence contract with Nada.
4. Final NBVE request/response contract with Rana.
5. Authentication and authorization integration with Seif.
6. Feedback and audit data contracts with Mohamed.
7. Future database schemas for permits, forecasts, verification cases, users, feedback, and audit records.

## 15. Document Maintenance
Update this document when implementation changes or when team integration requirements are approved.

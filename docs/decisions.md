# Technical Decisions Document



## Project

Space-Based Infrastructure Intelligence Platform



## 1. Purpose



This document records the main technical decisions governing the Backend and GIS architecture.



It explains the technologies selected, their purposes, implementation status, and decisions that still require confirmation.



The document will be updated as the platform develops.



## 2. Backend Framework



**Decision:** Use Python with FastAPI.



**Reason:**

- FastAPI supports REST API development.

- Pydantic provides request and response validation.

- Automatic OpenAPI documentation simplifies API testing.

- Python provides access to established geospatial and data-processing libraries.



**Status:** Implemented.



## 3. Database and ORM



**Decision:** Use SQLAlchemy as the database ORM.



**Development configuration:** SQLite.



**Planned production configuration:** PostgreSQL with PostGIS.



**Reason:**

- SQLAlchemy provides structured database models and session management.

- SQLite supports local development and automated testing.

- PostgreSQL provides a suitable production database.

- PostGIS will support spatial queries and geographic operations.



**Status:**

- SQLAlchemy: Implemented.

- SQLite: Implemented.

- PostgreSQL: Pending.

- PostGIS: Pending.



## 4. Geospatial Processing



**Decision:** Use Python geospatial libraries.



Selected libraries:



- Rasterio: Raster metadata extraction and raster processing.

- Shapely: Geometry validation and spatial operations.

- GeoPandas: Geospatial data manipulation.

- GeoAlchemy2: Planned SQLAlchemy integration with spatial database types.



**Reason:**



These libraries provide functionality for satellite image metadata processing, geographic validation, and future spatial database integration.



**Status:**

- Rasterio: Used in the image registration implementation.

- Shapely: Used in monitoring area geometry validation.

- GeoPandas: Available for future geospatial processing.

- GeoAlchemy2: Planned for PostGIS integration.



## 5. Coordinate Reference Systems



**Decision:** Use EPSG:4326 for monitoring area boundaries in the current API.



**Coordinate order:** Longitude followed by latitude for GeoJSON coordinates.



**Reason:**



EPSG:4326 provides a geographic coordinate reference system suitable for representing monitoring area boundaries and exchanging GeoJSON data.



Satellite image metadata retains the CRS associated with each raster.



Before and after images used in a detection must have matching CRS information.



**Status:**

- Monitoring area EPSG:4326 validation: Implemented.

- Satellite image CRS metadata: Implemented.

- General CRS transformation pipeline: Pending.

- Explicit detection geometry CRS contract: Requires confirmation.



## 6. Geographic Geometry Storage



**Current decision:** Store geographic geometry in JSON database columns during the initial development phase.



**Planned improvement:** Use native PostGIS geometry columns in the production database.



**Reason:**



JSON geometry supports the current development implementation, while PostGIS will provide spatial indexing and more efficient geographic queries.



**Status:**

- JSON geometry storage: Implemented.

- PostGIS geometry storage: Pending.

- Spatial indexing: Pending.



## 7. Satellite Image File Management



**Decision:** Store satellite image metadata and file references in the database rather than storing large raster files directly in database rows.



**Reason:**

- Raster files can be large.

- Separating metadata from file storage improves maintainability.

- Original satellite imagery must remain unchanged.

- File references allow the processing pipeline to locate approved source imagery.



**Status:** Metadata registration and file references are implemented. The final production file or object storage solution remains to be confirmed.



## 8. API Architecture



**Decision:** Use versioned REST APIs with JSON request and response formats.



**Current API prefix:** `/api/v1/`



**Reason:**

- Versioning supports future API changes.

- JSON provides a common interface between team components.

- Separate endpoints allow independent development and testing.



**Currently implemented resources:**

- Satellite images.

- Monitoring areas.

- Detections.



**Planned resources:**

- Infrastructure assets.

- Permit records.

- Verification cases.

- Dashboard data.



**Status:** Initial API architecture implemented. Additional endpoints and team integration contracts remain pending.



## 9. Data Validation and Integrity



**Decision:** Apply validation at both API and database levels where appropriate.



**Technologies:**

- Pydantic for API request validation.

- Shapely for geometry validation.

- SQLAlchemy for database operations.

- Database constraints for persistent data integrity.



**Current validation rules include:**

- Positive satellite image dimensions.

- Valid monitoring area geometry.

- Allowed monitoring area CRS.

- Valid before-and-after image relationships.

- Confidence scores between 0 and 1.

- Valid detection origin categories.



**Status:** Initial validation rules implemented. Additional database relationships and spatial constraints remain pending.



## 10. Timestamp Standards



**Decision:** Use timezone-aware timestamps, preferably normalized to UTC, throughout the platform.



**Reason:**



Satellite images may originate from different sources and time zones. Consistent timestamps are important when comparing acquisition dates and processing historical observations.



**Status:** Satellite image acquisition timestamps require timezone-aware values. Detection timestamp validation and consistent UTC normalization require further implementation.



## 11. Evidence Integrity and Security



**Decision:** Preserve original satellite evidence and restrict access to approved datasets.



**Rules:**

- Original satellite imagery must not be modified.

- Restricted information must not be committed to GitHub.

- Permit records require separate authorization.

- Detection confidence and model version information must be retained.

- Important system actions should be auditable.

- Verification recommendations must remain subject to human review.



**Status:** Data-handling constraints are documented. Full security and audit integration depends on the relevant team components.



## 12. Team Integration Strategy



**Decision:** Use documented API contracts between independently developed components.



**Integration dependencies:**



- Nada: AI detection output and evidence-quality fields.

- Rana: Next-Best-Verification Engine request and response formats.

- Seif: Authentication, authorization, and restricted-data requirements.

- Mohamed: Feedback and audit event requirements.

- Sandy: Backend APIs, GIS processing, and database integration.



The Backend and GIS component will provide the required APIs and data persistence.



Temporary mock data may be used for independent backend testing until the actual component contracts are agreed upon.



**Status:** Initial backend APIs are implemented. Final integration contracts remain pending.



## 13. Human-in-the-Loop Decision Making



**Decision:** The platform will provide decision support rather than autonomous legal or enforcement decisions.



**Reason:**



Satellite-based change detection may contain uncertainty. A missing permit record does not establish illegal construction, and AI predictions should not independently determine enforcement actions.



Authorized reviewers must evaluate relevant evidence before making operational decisions.



**Status:** Adopted as a project design constraint.



## 14. Pending Technical Decisions



The following items require further implementation or team agreement:



1. Final PostgreSQL and PostGIS production configuration.

2. Satellite raster file and object storage solution.

3. Spatial geometry types and indexing strategy.

4. Monitoring area foreign key enforcement.

5. Explicit CRS contract for detection geometry.

6. Standardized UTC timestamp validation.

7. Final AI detection API contract.

8. Final NBVE API contract.

9. Authentication and authorization integration.

10. Feedback and audit data contracts.



## 15. Document Maintenance



This document represents the current Backend and GIS technical decisions.



Decisions will be updated when implementation changes, team integration requirements are finalized, or new technical requirements are approved.

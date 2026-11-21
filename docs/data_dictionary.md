

# Data Dictionary



## Project

Space-Based Infrastructure Intelligence Platform



## 1. Purpose



This document defines the database structure, fields, data types, constraints, relationships, and validation rules used by the Backend and GIS components.



It describes the currently implemented SQLAlchemy database models and their corresponding Pydantic API schemas.



Implemented database entities are distinguished from planned entities to ensure that the documentation accurately reflects the current system.



## 2. Database Configuration



| Property | Current Configuration |

|---|---|

| ORM | SQLAlchemy |

| Database | SQLite (development) |

| Default database file | space_infra_dev.sqlite3 |

| Production database | PostgreSQL |

| Planned spatial extension | PostGIS |

| API validation | Pydantic |

| GIS geometry processing | Shapely |

| Database session | SessionLocal |

| Declarative base | Base |



The production database is intended to use PostgreSQL with PostGIS.



The current implementation stores geographic geometry in JSON columns rather than native PostGIS geometry columns.



## 3. Implemented Database Entities



### 3.1 MonitoringArea



**Table name:** `monitoring_areas`



**SQLAlchemy model:** `MonitoringAreaDB`



**Purpose:** Stores the geographic boundaries of areas selected for infrastructure monitoring.



| Field | Database Type | Constraint | Description |

|---|---|---|---|

| id | Integer | Primary Key, Auto Increment | Unique monitoring area identifier |

| name | VARCHAR(120) | NOT NULL | Monitoring area name |

| crs | VARCHAR(50) | NOT NULL | Coordinate Reference System |

| geometry | JSON | NOT NULL | Geographic boundary in GeoJSON-style format |



**API validation rules:**



- Name must contain at least one character.

- Name cannot exceed 120 characters.

- CRS is restricted to EPSG:4326.

- Geometry must be a Polygon or MultiPolygon.

- Geometry must not be empty.

- Geometry must be valid according to Shapely.

- Longitude must be between -180 and 180.

- Latitude must be between -90 and 90.

- GeoJSON coordinate order is longitude, latitude.



**API schemas:**



- MonitoringAreaCreate

- MonitoringAreaResponse



**Implemented endpoints:**



- POST /api/v1/monitoring-areas

- GET /api/v1/monitoring-areas

- GET /api/v1/monitoring-areas/{area_id}



### 3.2 SatelliteImage



**Table name:** `satellite_images`



**SQLAlchemy model:** `SatelliteImageDB`



**Purpose:** Stores metadata and file references for satellite images used in infrastructure monitoring.



| Field | Database Type | Constraint | Description |

|---|---|---|---|

| id | Integer | Primary Key, Auto Increment | Unique satellite image identifier |

| monitoring_area_id | Integer | NOT NULL | Identifier of the associated monitoring area |

| provider | VARCHAR(120) | NOT NULL | Satellite imagery provider |

| file_reference | VARCHAR(512) | NOT NULL | Location or reference of the raster file |

| acquired_at | DateTime(timezone=True) | NOT NULL | Image acquisition timestamp |

| crs | VARCHAR(120) | NOT NULL | Image coordinate reference system |

| width | Integer | NOT NULL | Raster image width in pixels |

| height | Integer | NOT NULL | Raster image height in pixels |

| band_count | Integer | NOT NULL | Number of raster bands |



**API validation rules:**



- monitoring_area_id must be greater than zero.

- Provider must not be empty.

- File reference must not be empty.

- Acquisition timestamp must be timezone-aware.

- CRS must not be empty.

- Width, height, and band count must be positive integers.



**API schemas:**



- SatelliteImageCreate

- SatelliteImageResponse



**Important database relationship note:**



The current model defines monitoring_area_id as an Integer, but it does not yet declare a ForeignKey to monitoring_areas.id.



The intended relationship is:



MONITORING_AREA (1) ---- (Many) SATELLITE_IMAGE



This relationship must be enforced through a future database migration.



### 3.3 Detection



**Table name:** `detections`



**SQLAlchemy model:** `DetectionDB`



**Purpose:** Stores detected geographic changes and their associated satellite image references.



| Field | Database Type | Constraint | Description |

|---|---|---|---|

| id | VARCHAR(36) | Primary Key | Unique detection identifier |

| before_image_id | Integer | Foreign Key, NOT NULL, Indexed | Reference to the earlier satellite image |

| after_image_id | Integer | Foreign Key, NOT NULL, Indexed | Reference to the later satellite image |

| observed_at | DateTime(timezone=True) | NOT NULL | Detection observation timestamp |

| geometry | JSON | NOT NULL | Geographic detection geometry |

| origin_category | VARCHAR(30) | NOT NULL | Classification of the detected change |

| confidence | Float | NOT NULL, CHECK 0 to 1 | Confidence score |

| model_version | VARCHAR(120) | NOT NULL | Version identifier of the model producing the detection |



**Foreign Key relationships:**



- before_image_id references satellite_images.id.

- after_image_id references satellite_images.id.



**Allowed origin categories:**



- human_made

- natural

- uncertain



**API validation rules:**



- Both image identifiers must be positive.

- Geometry must use Point type.

- Coordinates are represented as longitude and latitude.

- Origin category must be one of the three allowed values.

- Confidence must be between 0 and 1.

- Model version must not be empty.



**Additional detection validation in the API:**



- Before and after images must be different.

- Both referenced images must exist.

- Both images must belong to the same monitoring area.

- The before image must have an earlier acquisition timestamp.

- Both images must use the same CRS.



**Database constraint:**



The confidence field has a database CHECK constraint:



confidence >= 0 AND confidence <= 1



**API schemas:**



- DetectionCreate

- DetectionResponse



### 3.4 InfrastructureAsset

**Table name:** `infrastructure_assets`

**SQLAlchemy model:** `InfrastructureAssetDB`

**Purpose:** Stores infrastructure assets associated with monitoring areas, including their names, types, and geographic locations.

| Field | Database Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key, Auto Increment | Unique infrastructure asset identifier |
| monitoring_area_id | Integer | Foreign Key, NOT NULL, Indexed | Associated monitoring area |
| asset_name | VARCHAR(120) | NOT NULL | Infrastructure asset name |
| asset_type | VARCHAR(80) | NOT NULL | Infrastructure category |
| location | JSON | NOT NULL | Geographic location in GeoJSON format |

**Foreign Key relationship:**

- monitoring_area_id references monitoring_areas.id.
- The foreign key uses ON DELETE RESTRICT.

**Supported geometry types:**

- Point
- MultiPoint
- LineString
- MultiLineString
- Polygon
- MultiPolygon

**API validation rules:**

- Monitoring area identifier must be positive.
- The referenced monitoring area must exist.
- Asset name must not be empty and cannot exceed 120 characters.
- Asset type must not be empty and cannot exceed 80 characters.
- Geometry must use a supported GeoJSON type.
- Geometry must not be empty or invalid.
- Longitude must be between -180 and 180.
- Latitude must be between -90 and 90.
- The complete asset geometry must be covered by its monitoring area.
- Asset coordinates must use a coordinate system compatible with the associated monitoring area.

**API schemas:**

- InfrastructureAssetCreate
- InfrastructureAssetResponse

**Implemented endpoints:**

- POST /api/v1/infrastructure-assets
- GET /api/v1/infrastructure-assets
- GET /api/v1/infrastructure-assets/{asset_id}

**GIS validation:**

Shapely is used to validate geometry and check whether the complete asset geometry is covered by the associated monitoring area using the covers() operation.



## 4. Entity Relationships



### Current Database Relationships



```mermaid

MONITORING_AREA ||--o{ INFRASTRUCTURE_ASSET : contains

INFRASTRUCTURE_ASSET {
    int id PK
    int monitoring_area_id FK
    string asset_name
    string asset_type
    json location
}

erDiagram

       SATELLITE_IMAGE ||--o{ DETECTION : before_image

       SATELLITE_IMAGE ||--o{ DETECTION : after_image



       MONITORING_AREA {

           int id PK

           string name

           string crs

           json geometry

       }



       SATELLITE_IMAGE {

           int id PK

           int monitoring_area_id

           string provider

           string file_reference

           datetime acquired_at

           string crs

           int width

           int height

           int band_count

       }



       DETECTION {

           string id PK

           int before_image_id FK

           int after_image_id FK

           datetime observed_at

           json geometry

           string origin_category

           float confidence

           string model_version

       }

```



**Important:** The diagram shows the currently enforced foreign keys. The monitoring area relationship is an intended logical relationship and is not yet enforced by a database foreign key.



## 5. Geographic Data Standards



| Property | Standard |

|---|---|

| Monitoring area geometry | Polygon or MultiPolygon |

| Detection geometry | Point |

| Monitoring area CRS | EPSG:4326 |

| GeoJSON coordinate order | Longitude, Latitude |

| Geometry storage | JSON |

| Geometry validation | Shapely |

| Planned spatial storage | PostGIS geometry |



The current system uses EPSG:4326 for monitoring area boundaries.



Satellite images retain their own CRS metadata. Detection creation currently requires before and after images to have matching CRS information.



Native PostGIS geometry storage and spatial indexing remain future implementation tasks.



## 6. Data Integrity Rules



1. Every database entity must have a unique identifier.

2. Required database fields must not contain NULL values.

3. Satellite image dimensions must be positive.

4. Monitoring area boundaries must be valid.

5. Detection confidence must remain between 0 and 1.

6. Detections must reference existing satellite images.

7. Before and after images must represent different acquisition times.

8. Original satellite imagery must remain unchanged.

9. Restricted information must not be committed to GitHub.

10. Permit information must only be accessed through authorized sources.



## 7. Planned Database Entities



The following entities are part of the overall project architecture but are not implemented in the models reviewed in this document.



| Entity | Intended Purpose | Responsible Member / Integration |

|---|---|---|


| PermitRecord | Stores authorized permit information | Sandy / authorized data source |

| Forecast | Stores predicted future changes | Nada |

| VerificationCase | Stores verification cases and recommendations | Rana / Sandy backend integration |

| User | Stores user account information | Sandy / Seif integration |

| Feedback | Stores reviewer feedback | Mohamed |

| AuditLog | Records important system activities | Mohamed / Seif integration |



Their final schemas and relationships must be agreed upon before implementation.



## 8. Implementation Status



| Component | Status |

|---|---|

| MonitoringArea model | Implemented |

| SatelliteImage model | Implemented |

| Detection model | Implemented |

| Monitoring area API schemas | Implemented |

| Satellite image API schemas | Implemented |

| Detection API schemas | Implemented |

| Detection foreign keys | Implemented |

| Monitoring area foreign key enforcement | Pending |

| InfrastructureAsset model | Implemented |
| InfrastructureAsset API schemas | Implemented |
| InfrastructureAsset API endpoints | Implemented |
| InfrastructureAsset foreign key | Implemented |
| InfrastructureAsset GIS geometry validation | Implemented |
| PostgreSQL integration | Pending |

| PostGIS geometry storage | Pending |

| Spatial indexes | Pending |

| Remaining team database entities | Pending integration |



## 9. Future Improvements



The following improvements are planned:



- Enforce the monitoring area foreign key.


- Migrate the development database to PostgreSQL.

- Replace JSON geometry columns with PostGIS geometry columns.

- Introduce spatial indexes for geographic queries.

- Standardize timezone-aware timestamp validation.

- Add appropriate indexes for frequently queried fields.

- Implement database migrations to manage schema changes safely.



This document will be updated as the database architecture evolves.





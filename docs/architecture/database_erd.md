
# Database Design

## Project
Space-Based Infrastructure Intelligence Platform

## Initial Database Entities

The first backend implementation includes:

1. MonitoringArea
2. SatelliteImage
3. InfrastructureAsset
4. Detection

Additional entities for permits, forecasting,
verification cases, users, feedback, and audit
logging will be integrated with the responsible
team members.

## Entity Relationship Diagram

```mermaid
erDiagram
    MONITORING_AREA ||--o{ SATELLITE_IMAGE : contains
    MONITORING_AREA ||--o{ INFRASTRUCTURE_ASSET : contains
    SATELLITE_IMAGE ||--o{ DETECTION : before_image
    SATELLITE_IMAGE ||--o{ DETECTION : after_image

    MONITORING_AREA {
        int id PK
        string name
        geometry boundary
        string source
    }

    SATELLITE_IMAGE {
        int id PK
        int monitoring_area_id FK
        string file_reference
        string provider
        datetime acquired_at
        string crs
        int width
        int height
        int band_count
    }

    INFRASTRUCTURE_ASSET {
        int id PK
        int monitoring_area_id FK
        string asset_name
        string asset_type
        geometry location
    }

    DETECTION {
        int id PK
        int before_image_id FK
        int after_image_id FK
        geometry footprint
        string origin_category
        float confidence
        datetime detected_at
        string model_version
    }
```

## Data Design Rules

- Every entity has a unique identifier.
- Satellite images reference their monitoring area.
- Detections reference the before and after images.
- Geographic features use PostGIS geometry fields.
- Coordinate reference systems must be documented.
- Confidence scores range from 0 to 1.
- Original satellite files are referenced, not modified.
- Restricted data must not be committed to GitHub.

## Future Database Integration

The design will later include:

- PermitRecord
- Forecast
- VerificationCase
- User
- Feedback
- AuditLog

Their schemas must be agreed with the responsible
members before implementation.
```

# Detection Integration Contract — Current Backend Schema

**Status:** Backend schema snapshot; not a substitute for final AI-team approval.  
**Owner:** Backend & GIS (Sandy)  
**API:** `POST /api/v1/detections`

## Required fields

| Field | Type | Rules |
|---|---|---|
| before_image_id | integer | Positive; existing registered image |
| after_image_id | integer | Positive; different existing image |
| observed_at | datetime | Timezone-aware; normalized to UTC |
| geometry | GeoJSON geometry | Point, Polygon, or MultiPolygon |
| origin_category | string | `human_made`, `natural`, or `uncertain` |
| model_version | string | Non-empty |

## Optional fields

| Field | Type | Rules |
|---|---|---|
| component_id | integer or null | Greater than or equal to zero |
| confidence | number or null | 0 through 1; null is preserved |
| change_score | number or null | Optional numeric value |
| threshold | object or null | Optional structured metadata |
| pixel_count | integer or null | Greater than or equal to zero |
| area_m2 | number or null | Greater than or equal to zero |
| evidence_quality | object or null | Structured evidence-quality metadata |
| quality_flags | string array or null | Optional flags |
| mask_reference | string or null | Optional reference to a separately stored mask |

## Backend validation

1. Both image records must exist.
2. Images must belong to the same monitoring area.
3. The before image must have an earlier acquisition timestamp.
4. Both images must have matching CRS strings.
5. The detection geometry is normalized to EPSG:4326.
6. The complete geometry must be covered by the monitoring area.
7. `observed_at` must include timezone information.

## Example

```json
{
  "before_image_id": 1,
  "after_image_id": 2,
  "observed_at": "2026-11-20T10:00:00Z",
  "geometry": {"type": "Point", "coordinates": [31.05, 30.05]},
  "component_id": 8,
  "origin_category": "uncertain",
  "confidence": null,
  "change_score": 0.82,
  "threshold": {"value": 0.4},
  "pixel_count": 120,
  "area_m2": 12000,
  "evidence_quality": {"alignment": "checked"},
  "quality_flags": [],
  "mask_reference": "approved-storage-reference",
  "model_version": "image-differencing-baseline-v1.0.0"
}
```

## Contract boundaries and open questions

- This file documents fields accepted by the current backend, not a guarantee that every AI output field has been agreed with the AI owner.
- The backend does not infer confidence when it is absent.
- The backend does not reinterpret `uncertain` as a confirmed human-made or natural change.
- Any new fields or changed semantics must be agreed with the AI owner and recorded as a versioned contract update.
- Raster files and masks remain external to this JSON request; `mask_reference` is a reference, not an upload.

# AI–Backend Detection Integration Contract

## Status

Provisional integration contract.
The final format must be confirmed with the AI team.

## Backend Endpoints

- POST /api/v1/images
- GET /api/v1/images
- GET /api/v1/images/{image_id}
- POST /api/v1/detections
- GET /api/v1/detections

## Integration Workflow

1. Register the before-image metadata.
2. Register the after-image metadata.
3. Obtain the registered image IDs.
4. Run the AI model using the image pair.
5. Convert the AI prediction into a DetectionCreate request.
6. Submit the detection through POST /api/v1/detections.
7. Retrieve stored detections using GET /api/v1/detections.

## Detection Request

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
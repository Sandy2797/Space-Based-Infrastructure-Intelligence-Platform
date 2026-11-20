
from fastapi import APIRouter, HTTPException

from app.schemas.satellite_image import (
    SatelliteImageCreate,
    SatelliteImageResponse,
)

router = APIRouter(
    prefix="/api/v1/images",
    tags=["Satellite Images"],
)

# Temporary storage until PostgreSQL is available.
mock_images: list[SatelliteImageResponse] = []


@router.post(
    "",
    response_model=SatelliteImageResponse,
    status_code=201,
)
def register_image(image: SatelliteImageCreate):
    image_id = len(mock_images) + 1

    record = SatelliteImageResponse(
        id=image_id,
        **image.model_dump(),
    )

    mock_images.append(record)

    return record


@router.get(
    "",
    response_model=list[SatelliteImageResponse],
)
def get_images():
    return mock_images


@router.get(
    "/{image_id}",
    response_model=SatelliteImageResponse,
)
def get_image(image_id: int):
    for image in mock_images:
        if image.id == image_id:
            return image

    raise HTTPException(
        status_code=404,
        detail="Satellite image not found",
    )


from datetime import datetime
from pathlib import Path

from app.schemas.satellite_image import SatelliteImageCreate
from app.services.raster_service import read_image_metadata


def prepare_image_registration(
    file_path: str | Path,
    monitoring_area_id: int,
    provider: str,
    acquired_at: datetime,
) -> SatelliteImageCreate:
    """
    Read a local GeoTIFF and prepare its registration data.

    The original satellite image is not modified.
    """

    metadata = read_image_metadata(file_path)

    # A satellite image needs geographic reference information.
    if metadata["crs"] is None:
        raise ValueError(
            "Satellite image has no coordinate reference system"
        )

    # Create the registration record using extracted metadata.
    return SatelliteImageCreate(
        monitoring_area_id=monitoring_area_id,
        provider=provider,
        file_reference=Path(file_path).name,
        acquired_at=acquired_at,
        crs=metadata["crs"],
        width=metadata["width"],
        height=metadata["height"],
        band_count=metadata["band_count"],
    )

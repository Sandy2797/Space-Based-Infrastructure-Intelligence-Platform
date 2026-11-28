
from pydantic import BaseModel, Field, AwareDatetime


class SatelliteImageCreate(BaseModel):
    monitoring_area_id: int = Field(gt=0)

    provider: str = Field(min_length=1)
    file_reference: str = Field(min_length=1)

    acquired_at: AwareDatetime

    crs: str = Field(min_length=1)

    width: int = Field(gt=0)
    height: int = Field(gt=0)
    band_count: int = Field(gt=0)


class SatelliteImageResponse(SatelliteImageCreate):
    id: int

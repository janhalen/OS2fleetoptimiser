from celery.states import ALL_STATES

from datetime import datetime

from pydantic import BaseModel
from typing import List, Literal


class AllowedStartAddition(BaseModel):
    id: int | None  # have to be nullable in order to create new
    latitude: float
    longitude: float
    allowed_start_id: int | None  # have to be nullable in order to create new
    addition_date: datetime | None  # have to be nullable in order to create new


class AllowedStartPrecision(BaseModel):
    id: int
    precision: float
    roundtrip_km: float
    km: float


class AllowedStart(BaseModel):
    id: int | None  # have to be nullable in order to create new
    address: str
    latitude: float
    longitude: float
    additional_starts: None | List[AllowedStartAddition]
    car_count: None | int
    addition_date: datetime | None

    # todo add addition date so we can track and display that in frontend
    def to_extended_info(self, precision: AllowedStartPrecision = None) -> 'ExtendedLocationInformation':
        return ExtendedLocationInformation(
            **self.dict(),
            precision=precision.precision if precision else 0,
            roundtrip_km=precision.roundtrip_km if precision else 0,
            km=precision.km if precision else 0
        )


class ExtendedLocationInformation(AllowedStart):
    precision: float
    roundtrip_km: float
    km: float


class PrecisionTestIn(BaseModel):
    location: int
    test_specific_start: AllowedStart
    start_date: datetime


class PrecisionTestOptions(PrecisionTestIn):
    extractors: list[str]
    test_name: str


class PrecisionTestResults(AllowedStartPrecision):
    test_settings: PrecisionTestIn


class PrecisionTestOut(BaseModel):
    id: str
    status: Literal[tuple(ALL_STATES) + ("PROGRESS",)]
    progress: dict | None
    result: PrecisionTestResults | None


class LocationName(BaseModel):
    location_id: int
    address: str

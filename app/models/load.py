"""
Pydantic models for load data.
"""

from pydantic import BaseModel
from typing import Optional


class Load(BaseModel):
    """Model representing a single freight load."""

    load_id: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    equipment_type: str
    loadboard_rate: float
    notes: Optional[str] = None
    weight: Optional[float] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: Optional[str] = None


class LoadSearchParams(BaseModel):
    """Query parameters for load search."""

    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment_type: Optional[str] = None
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    pickup_date: Optional[str] = None


class LoadSearchResponse(BaseModel):
    """Response model for load search."""

    total_results: int
    loads: list[Load]
    message: str = ""

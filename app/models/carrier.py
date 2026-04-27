"""
Pydantic models for carrier verification.
"""

from pydantic import BaseModel
from typing import Optional


class CarrierVerification(BaseModel):
    """Response model for carrier MC number verification."""

    mc_number: str
    legal_name: Optional[str] = None
    dot_number: Optional[str] = None
    operating_status: Optional[str] = None
    is_eligible: bool = False
    entity_type: Optional[str] = None
    phone: Optional[str] = None
    safety_rating: Optional[str] = None
    out_of_service: Optional[bool] = None
    message: str = ""


class CarrierError(BaseModel):
    """Error response for carrier lookup."""

    mc_number: str
    is_eligible: bool = False
    message: str

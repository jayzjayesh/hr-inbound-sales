"""
Carrier verification route — looks up MC numbers via FMCSA API.
"""

from fastapi import APIRouter, Depends, Query
from app.auth.api_key import verify_api_key
from app.services.fmcsa import verify_carrier_by_mc
from app.models.carrier import CarrierVerification, CarrierError

router = APIRouter(prefix="/api/v1", tags=["Carrier"])


@router.get(
    "/carrier",
    response_model=CarrierVerification | CarrierError,
    summary="Verify a carrier by MC number",
    description="Looks up a carrier's MC (docket) number against the FMCSA database "
    "and returns eligibility status, safety rating, and company details.",
)
async def get_carrier(
    mc_number: str = Query(..., description="The carrier's MC number"),
    _: str = Depends(verify_api_key),
):
    """
    Verify a carrier by their MC number.

    The HappyRobot agent calls this tool when a carrier provides their MC number.
    Returns whether the carrier is authorized to operate and eligible to haul loads.
    """
    result = await verify_carrier_by_mc(mc_number)
    return result


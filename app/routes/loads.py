"""
Load search route — searches available loads for carriers.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth.api_key import verify_api_key
from app.services.load_service import search_loads, get_load_by_id
from app.models.load import Load, LoadSearchResponse

router = APIRouter(prefix="/api/v1", tags=["Loads"])


@router.get(
    "/loads",
    response_model=LoadSearchResponse,
    summary="Search available loads",
    description="Search for available freight loads by origin, destination, equipment type, "
    "rate range, and pickup date. Returns up to 5 best-matching loads sorted by rate.",
)
async def find_loads(
    load_id: Optional[str] = Query(None, description="Load ID to look up directly (e.g., LD-1001)"),
    origin: Optional[str] = Query(None, description="Origin city or state (fuzzy match)"),
    destination: Optional[str] = Query(None, description="Destination city or state (fuzzy match)"),
    equipment_type: Optional[str] = Query(None, description="Equipment type: Van, Reefer, Flatbed, etc."),
    min_rate: Optional[float] = Query(None, description="Minimum rate in USD"),
    max_rate: Optional[float] = Query(None, description="Maximum rate in USD"),
    pickup_date: Optional[str] = Query(None, description="Pickup date (YYYY-MM-DD)"),
    _: str = Depends(verify_api_key),
):
    """
    Search for available loads matching carrier criteria.

    The HappyRobot agent calls this tool when a carrier asks about available loads.
    Supports direct lookup by load_id, or fuzzy search by origin/destination/equipment.
    """
    # Direct lookup by load ID if provided
    if load_id:
        load = get_load_by_id(load_id)
        if load:
            return LoadSearchResponse(
                total_results=1,
                loads=[load],
                message=f"Found load {load_id}.",
            )
        return LoadSearchResponse(
            total_results=0,
            loads=[],
            message=f"No load found with ID {load_id}. Try searching by lane instead.",
        )

    result = search_loads(
        origin=origin,
        destination=destination,
        equipment_type=equipment_type,
        min_rate=min_rate,
        max_rate=max_rate,
        pickup_date=pickup_date,
    )
    return result


@router.get(
    "/loads/{load_id}",
    response_model=Load,
    summary="Get a specific load by ID",
    description="Retrieve full details for a specific load by its unique identifier.",
)
async def get_load(
    load_id: str,
    _: str = Depends(verify_api_key),
):
    """Get a specific load by its ID."""
    load = get_load_by_id(load_id)
    if not load:
        raise HTTPException(status_code=404, detail=f"Load {load_id} not found.")
    return load

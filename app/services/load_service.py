"""
Load search service — loads data from JSON and provides fuzzy search.
"""

import json
import logging
from pathlib import Path
from typing import Optional
from app.models.load import Load, LoadSearchResponse

logger = logging.getLogger(__name__)

# In-memory load database
_loads: list[Load] = []


def init_loads(data_path: str = "data/loads.json") -> None:
    """Load the load database from a JSON file into memory."""
    global _loads
    path = Path(data_path)

    if not path.exists():
        logger.error(f"Load data file not found: {data_path}")
        _loads = []
        return

    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    _loads = [Load(**item) for item in raw_data]
    logger.info(f"Loaded {len(_loads)} loads from {data_path}")


def _fuzzy_match(field_value: str, query: str) -> bool:
    """
    Case-insensitive partial match.
    E.g., query='dallas' matches 'Dallas, TX' or 'Dallas - Fort Worth, TX'.
    """
    return query.strip().lower() in field_value.strip().lower()


def search_loads(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment_type: Optional[str] = None,
    min_rate: Optional[float] = None,
    max_rate: Optional[float] = None,
    pickup_date: Optional[str] = None,
) -> LoadSearchResponse:
    """
    Search loads with optional filters. Returns up to 5 best matches.

    Args:
        origin: Fuzzy match on origin city/state.
        destination: Fuzzy match on destination city/state.
        equipment_type: Exact match on equipment type (case-insensitive).
        min_rate: Minimum rate filter.
        max_rate: Maximum rate filter.
        pickup_date: Date filter (matches date portion of pickup_datetime).

    Returns:
        LoadSearchResponse with matching loads.
    """
    results = list(_loads)

    # Apply filters
    if origin:
        results = [l for l in results if _fuzzy_match(l.origin, origin)]

    if destination:
        results = [l for l in results if _fuzzy_match(l.destination, destination)]

    if equipment_type:
        results = [
            l
            for l in results
            if l.equipment_type.strip().lower() == equipment_type.strip().lower()
        ]

    if min_rate is not None:
        results = [l for l in results if l.loadboard_rate >= min_rate]

    if max_rate is not None:
        results = [l for l in results if l.loadboard_rate <= max_rate]

    if pickup_date:
        results = [l for l in results if pickup_date in l.pickup_datetime]

    # Sort by rate descending (best paying first) and limit to 5
    results.sort(key=lambda l: l.loadboard_rate, reverse=True)
    top_results = results[:5]

    if not top_results:
        message = "No loads found matching your criteria. Try broadening your search."
    elif len(top_results) == 1:
        message = f"Found 1 load matching your criteria."
    else:
        message = f"Found {len(results)} loads. Showing top {len(top_results)}."

    return LoadSearchResponse(
        total_results=len(results),
        loads=top_results,
        message=message,
    )


def get_load_by_id(load_id: str) -> Optional[Load]:
    """Look up a specific load by its ID."""
    for load in _loads:
        if load.load_id == load_id:
            return load
    return None

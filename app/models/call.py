"""
Pydantic models for call data.
"""

from pydantic import BaseModel
from typing import Optional


class CallRecord(BaseModel):
    """Data received from HappyRobot after a call."""

    mc_number: Optional[str] = None
    carrier_name: Optional[str] = None
    load_id: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment_type: Optional[str] = None
    loadboard_rate: Optional[float] = None
    agreed_rate: Optional[float] = None
    negotiation_rounds: Optional[int] = 0
    call_outcome: Optional[str] = None
    carrier_sentiment: Optional[str] = None
    call_summary: Optional[str] = None
    call_duration: Optional[int] = 0


class CallResponse(BaseModel):
    """Response after storing a call record."""

    id: int
    message: str


class MetricsResponse(BaseModel):
    """Aggregated metrics for the dashboard."""

    total_calls: int
    success_rate: float
    avg_revenue: float
    avg_negotiation_savings: float
    outcomes: dict
    sentiments: dict
    calls_over_time: list
    top_lanes: list
    negotiation_data: list
    recent_calls: list

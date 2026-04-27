"""
Call data routes — receives post-call data and serves metrics.
"""

from fastapi import APIRouter, Depends
from app.auth.api_key import verify_api_key
from app.database import get_db
from app.models.call import CallRecord, CallResponse, MetricsResponse

router = APIRouter(prefix="/api/v1", tags=["Calls"])


@router.post(
    "/calls",
    response_model=CallResponse,
    summary="Record a completed call",
    description="Receives post-call data from HappyRobot's Extract node and stores it.",
)
async def create_call(
    call: CallRecord,
    _: str = Depends(verify_api_key),
):
    """Store a new call record from HappyRobot."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO calls (
                mc_number, carrier_name, load_id, origin, destination,
                equipment_type, loadboard_rate, agreed_rate, negotiation_rounds,
                call_outcome, carrier_sentiment, call_summary, call_duration
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                call.mc_number,
                call.carrier_name,
                call.load_id,
                call.origin,
                call.destination,
                call.equipment_type,
                call.loadboard_rate,
                call.agreed_rate,
                call.negotiation_rounds,
                call.call_outcome,
                call.carrier_sentiment,
                call.call_summary,
                call.call_duration,
            ),
        )
        call_id = cursor.lastrowid

    return CallResponse(id=call_id, message="Call record stored successfully.")


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Get dashboard metrics",
    description="Returns aggregated metrics for all calls — outcomes, sentiment, "
    "negotiation performance, revenue, and recent call history.",
)
async def get_metrics():
    """
    Aggregate call data into dashboard metrics.
    No API key required — dashboard is public.
    """
    with get_db() as conn:
        # Total calls
        total = conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]

        if total == 0:
            return MetricsResponse(
                total_calls=0,
                success_rate=0.0,
                avg_revenue=0.0,
                avg_negotiation_savings=0.0,
                outcomes={},
                sentiments={},
                calls_over_time=[],
                top_lanes=[],
                negotiation_data=[],
                recent_calls=[],
            )

        # Success rate
        successes = conn.execute(
            "SELECT COUNT(*) FROM calls WHERE call_outcome = 'Success'"
        ).fetchone()[0]
        success_rate = round((successes / total) * 100, 1) if total > 0 else 0

        # Average revenue (from agreed rates)
        avg_rev = conn.execute(
            "SELECT AVG(agreed_rate) FROM calls WHERE agreed_rate IS NOT NULL"
        ).fetchone()[0]
        avg_revenue = round(avg_rev, 2) if avg_rev else 0

        # Average negotiation savings
        savings_rows = conn.execute(
            """
            SELECT AVG(
                CASE WHEN loadboard_rate > 0 AND agreed_rate IS NOT NULL
                THEN ((loadboard_rate - agreed_rate) / loadboard_rate) * 100
                ELSE 0 END
            ) FROM calls WHERE agreed_rate IS NOT NULL
            """
        ).fetchone()[0]
        avg_savings = round(savings_rows, 1) if savings_rows else 0

        # Outcome distribution
        outcome_rows = conn.execute(
            "SELECT call_outcome, COUNT(*) as cnt FROM calls GROUP BY call_outcome"
        ).fetchall()
        outcomes = {row["call_outcome"]: row["cnt"] for row in outcome_rows}

        # Sentiment distribution
        sentiment_rows = conn.execute(
            "SELECT carrier_sentiment, COUNT(*) as cnt FROM calls GROUP BY carrier_sentiment"
        ).fetchall()
        sentiments = {row["carrier_sentiment"]: row["cnt"] for row in sentiment_rows}

        # Calls over time (by date)
        time_rows = conn.execute(
            """
            SELECT DATE(timestamp) as date, COUNT(*) as cnt
            FROM calls GROUP BY DATE(timestamp) ORDER BY date
            """
        ).fetchall()
        calls_over_time = [
            {"date": row["date"], "count": row["cnt"]} for row in time_rows
        ]

        # Top lanes
        lane_rows = conn.execute(
            """
            SELECT origin || ' → ' || destination as lane, COUNT(*) as cnt
            FROM calls WHERE origin IS NOT NULL AND destination IS NOT NULL
            GROUP BY lane ORDER BY cnt DESC LIMIT 8
            """
        ).fetchall()
        top_lanes = [
            {"lane": row["lane"], "count": row["cnt"]} for row in lane_rows
        ]

        # Negotiation data (for booked loads)
        neg_rows = conn.execute(
            """
            SELECT load_id, origin, destination, loadboard_rate, agreed_rate
            FROM calls
            WHERE agreed_rate IS NOT NULL AND loadboard_rate IS NOT NULL
            ORDER BY timestamp DESC LIMIT 10
            """
        ).fetchall()
        negotiation_data = [
            {
                "load_id": row["load_id"],
                "lane": f"{row['origin']} → {row['destination']}",
                "loadboard_rate": row["loadboard_rate"],
                "agreed_rate": row["agreed_rate"],
            }
            for row in neg_rows
        ]

        # Recent calls
        recent_rows = conn.execute(
            """
            SELECT timestamp, carrier_name, origin, destination,
                   equipment_type, call_outcome, carrier_sentiment,
                   loadboard_rate, agreed_rate, negotiation_rounds, call_duration
            FROM calls ORDER BY timestamp DESC LIMIT 20
            """
        ).fetchall()
        recent_calls = [
            {
                "timestamp": row["timestamp"],
                "carrier_name": row["carrier_name"] or "Unknown",
                "origin": row["origin"] or "N/A",
                "destination": row["destination"] or "N/A",
                "equipment_type": row["equipment_type"] or "N/A",
                "call_outcome": row["call_outcome"] or "Unknown",
                "carrier_sentiment": row["carrier_sentiment"] or "Unknown",
                "loadboard_rate": row["loadboard_rate"],
                "agreed_rate": row["agreed_rate"],
                "negotiation_rounds": row["negotiation_rounds"],
                "call_duration": row["call_duration"],
            }
            for row in recent_rows
        ]

    return MetricsResponse(
        total_calls=total,
        success_rate=success_rate,
        avg_revenue=avg_revenue,
        avg_negotiation_savings=avg_savings,
        outcomes=outcomes,
        sentiments=sentiments,
        calls_over_time=calls_over_time,
        top_lanes=top_lanes,
        negotiation_data=negotiation_data,
        recent_calls=recent_calls,
    )

"""
FMCSA API client for carrier verification.
"""

import httpx
import logging
from app.config import get_settings
from app.models.carrier import CarrierVerification, CarrierError

logger = logging.getLogger(__name__)


async def verify_carrier_by_mc(mc_number: str) -> CarrierVerification | CarrierError:
    """
    Look up a carrier by MC (docket) number using the FMCSA QCMobile API.

    Args:
        mc_number: The carrier's Motor Carrier number (digits only).

    Returns:
        CarrierVerification with eligibility info, or CarrierError on failure.
    """
    settings = get_settings()

    # Strip any non-numeric characters (carriers might say "MC-123456" or "MC 123456")
    clean_mc = "".join(filter(str.isdigit, mc_number))

    if not clean_mc:
        return CarrierError(
            mc_number=mc_number,
            is_eligible=False,
            message=f"Invalid MC number format: '{mc_number}'. Please provide a numeric MC number.",
        )

    url = f"{settings.FMCSA_BASE_URL}/carriers/docket-number/{clean_mc}"
    params = {"webKey": settings.FMCSA_API_KEY}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)

        if response.status_code == 404:
            return CarrierError(
                mc_number=clean_mc,
                is_eligible=False,
                message=f"No carrier found with MC number {clean_mc}.",
            )

        if response.status_code != 200:
            logger.error(f"FMCSA API error: {response.status_code} - {response.text}")
            return CarrierError(
                mc_number=clean_mc,
                is_eligible=False,
                message="Unable to verify carrier at this time. Please try again later.",
            )

        data = response.json()

        # The FMCSA API returns a 'content' wrapper with carrier records
        content = data.get("content", [])
        if not content:
            return CarrierError(
                mc_number=clean_mc,
                is_eligible=False,
                message=f"No carrier found with MC number {clean_mc}.",
            )

        carrier = content[0].get("carrier", content[0])

        # Extract key fields
        operating_status = carrier.get("allowedToOperate", "")
        legal_name = carrier.get("legalName", "Unknown")
        dot_number = str(carrier.get("dotNumber", ""))
        entity_type = carrier.get("entityType", "")
        phone = carrier.get("phyPhone", "")
        safety_rating = carrier.get("safetyRating", "Not Rated")
        oos = carrier.get("oosFlag", "N")

        # Carrier is eligible if they are authorized to operate
        is_eligible = str(operating_status).upper() == "Y"

        if is_eligible:
            message = f"Carrier '{legal_name}' (MC-{clean_mc}) is authorized and eligible to haul loads."
        else:
            message = f"Carrier '{legal_name}' (MC-{clean_mc}) is NOT authorized to operate. Status: {operating_status}."

        return CarrierVerification(
            mc_number=clean_mc,
            legal_name=legal_name,
            dot_number=dot_number,
            operating_status="AUTHORIZED" if is_eligible else str(operating_status),
            is_eligible=is_eligible,
            entity_type=entity_type,
            phone=phone,
            safety_rating=safety_rating if safety_rating else "Not Rated",
            out_of_service=str(oos).upper() == "Y",
            message=message,
        )

    except httpx.TimeoutException:
        logger.error(f"FMCSA API timeout for MC {clean_mc}")
        return CarrierError(
            mc_number=clean_mc,
            is_eligible=False,
            message="FMCSA API timed out. Please try again.",
        )
    except Exception as e:
        logger.error(f"FMCSA API unexpected error: {e}")
        return CarrierError(
            mc_number=clean_mc,
            is_eligible=False,
            message="An unexpected error occurred while verifying the carrier.",
        )

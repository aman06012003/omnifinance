"""Affiliate tracking and outbound redirect service."""
import logging
from typing import Optional
from sqlmodel import Session

from app.db.models import AffiliateClick
from app.countries.registry import country_registry

logger = logging.getLogger(__name__)

def record_affiliate_click(
    db: Session,
    partner_id: str,
    country_code: str = "fi",
    category: str = "general",
    page_path: str = "/",
) -> Optional[str]:
    """Logs the click event to SQLite and returns the target affiliate destination URL."""
    target_url = None
    pack = country_registry.get(country_code)

    if pack:
        for partner in pack.affiliates:
            if partner.id == partner_id:
                target_url = partner.url
                break

    if not target_url:
        logger.warning(f"Affiliate partner not found: {partner_id} in {country_code}")
        target_url = "/"

    try:
        click_record = AffiliateClick(
            partner_id=partner_id,
            category=category,
            country=country_code,
            page_path=page_path,
        )
        db.add(click_record)
        db.commit()
    except Exception as e:
        logger.error(f"Error recording affiliate click: {e}")

    return target_url

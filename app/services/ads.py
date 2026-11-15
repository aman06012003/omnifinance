"""AdSense and Monetization management."""
from typing import Optional
from app.config import settings

def render_ad_slot(slot_name: str, country_code: str = "fi") -> str:
    """Returns HTML for an ad slot if monetization is enabled and consent given."""
    if not settings.ENABLE_ADS:
        return f"""
        <!-- Ad Slot: {slot_name} (Monetization currently disabled) -->
        <div class="ad-placeholder-container" style="display: none;"></div>
        """

    client_id = settings.ADSENSE_CLIENT_ID
    return f"""
    <div class="ad-slot-wrapper my-6 text-center" data-slot="{slot_name}">
        <span class="text-xs text-muted block mb-1 uppercase tracking-wider">Advertisement</span>
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="{client_id}"
             data-ad-slot="1234567890"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
    </div>
    """

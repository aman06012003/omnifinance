"""Services package."""
from .i18n import get_translator, format_currency
from .affiliates import record_affiliate_click
from .ads import render_ad_slot
from .seo import generate_sitemap_xml, generate_robots_txt

__all__ = [
    "get_translator",
    "format_currency",
    "record_affiliate_click",
    "render_ad_slot",
    "generate_sitemap_xml",
    "generate_robots_txt",
]

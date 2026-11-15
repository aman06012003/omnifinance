"""SEO Service: Sitemap, Robots, and Structured Data generation."""
from typing import List, Dict, Any
from app.countries.registry import country_registry

def generate_sitemap_xml(base_url: str = "https://omnifinance.io") -> str:
    """Dynamically build sitemap.xml for all registered countries, languages, and calculators."""
    urls = [f"{base_url}/"]

    for pack in country_registry.get_all():
        for lang in pack.config.languages:
            # Country home
            urls.append(f"{base_url}/{pack.code}/{lang}/")
            # All enabled calculators
            for calc in pack.config.enabled_calculators:
                urls.append(f"{base_url}/{pack.code}/{lang}/{calc}/")
            # Affiliate comparisons
            for cat in ["brokers", "mortgages", "loans"]:
                urls.append(f"{base_url}/{pack.code}/{lang}/compare/{cat}/")

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        xml_lines.append(f"  <url><loc>{u}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>")
    xml_lines.append('</urlset>')

    return "\n".join(xml_lines)

def generate_robots_txt(base_url: str = "https://omnifinance.io") -> str:
    """Generate robots.txt adhering to AdSense and crawler standards."""
    return f"""User-agent: *
Allow: /
Disallow: /go/
Disallow: /healthz

Sitemap: {base_url}/sitemap.xml
"""

def generate_schema_org_calculator(
    calculator_name: str,
    description: str,
    url: str,
    currency: str = "EUR",
) -> Dict[str, Any]:
    """Return JSON-LD structured data for Financial Calculator tool."""
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": calculator_name,
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "All",
        "url": url,
        "description": description,
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": currency,
        },
    }

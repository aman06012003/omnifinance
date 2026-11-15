"""SEO and health check endpoints."""
from fastapi import APIRouter, Response
from app.services.seo import generate_sitemap_xml, generate_robots_txt
from app.config import settings

router = APIRouter()

@router.get("/sitemap.xml", response_class=Response)
async def sitemap():
    """Returns XML sitemap for search crawlers."""
    xml_content = generate_sitemap_xml()
    return Response(content=xml_content, media_type="application/xml")

@router.get("/robots.txt", response_class=Response)
async def robots():
    """Returns robots.txt."""
    content = generate_robots_txt()
    return Response(content=content, media_type="text/plain")

@router.get("/ads.txt", response_class=Response)
async def ads_txt():
    """Returns Google AdSense publisher authorization file."""
    client_id = settings.ADSENSE_CLIENT_ID.replace("ca-", "")
    content = f"google.com, {client_id}, DIRECT, f08c47fec0942fa0\n"
    return Response(content=content, media_type="text/plain")

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Empty 204 response for browser default favicon request."""
    return Response(status_code=204)

@router.get("/healthz")
async def health_check():
    """Standard health check endpoint for cloud platforms and load balancers."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "groq_live": bool(settings.GROQ_API_KEY and not settings.GROQ_API_KEY.startswith("gsk_your_groq")),
    }

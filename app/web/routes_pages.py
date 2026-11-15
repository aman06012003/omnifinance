"""Static and high-level platform pages."""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.config import settings
from app.countries.registry import country_registry
from app.services.i18n import get_translator
from app.services.affiliates import record_affiliate_click
from app.db.session import get_session

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

@router.get("/", response_class=HTMLResponse)
async def platform_index(request: Request):
    """Platform landing and global country selector."""
    all_packs = country_registry.get_all()
    default_pack = country_registry.get(settings.DEFAULT_COUNTRY) or (all_packs[0] if all_packs else None)
    lang = settings.DEFAULT_LANGUAGE
    t = get_translator(lang)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "all_countries": all_packs,
            "current_country_pack": default_pack,
            "country_code": default_pack.code if default_pack else "fi",
            "lang": lang,
            "t": t,
            "active_page": "global",
        },
    )

@router.get("/{country}/{lang}/", response_class=HTMLResponse)
async def country_home(country: str, lang: str, request: Request):
    """Country-specific portal hub."""
    pack = country_registry.get(country)
    if not pack:
        raise HTTPException(status_code=404, detail="Country pack not found")

    all_packs = country_registry.get_all()
    t = get_translator(lang)

    return templates.TemplateResponse(
        request=request,
        name="country_home.html",
        context={
            "all_countries": all_packs,
            "current_country_pack": pack,
            "country_code": pack.code,
            "lang": lang,
            "t": t,
            "active_page": "home",
        },
    )

@router.get("/{country}/{lang}/compare/{category}/", response_class=HTMLResponse)
async def affiliate_comparison(country: str, lang: str, category: str, request: Request):
    """Comparison table for financial providers (brokers, mortgages, loans)."""
    pack = country_registry.get(country)
    if not pack:
        raise HTTPException(status_code=404, detail="Country pack not found")

    all_packs = country_registry.get_all()
    t = get_translator(lang)

    # Filter partners by category
    partners = [p for p in pack.affiliates if p.category == category]

    return templates.TemplateResponse(
        request=request,
        name="comparison.html",
        context={
            "all_countries": all_packs,
            "current_country_pack": pack,
            "country_code": pack.code,
            "lang": lang,
            "category": category,
            "partners": partners,
            "t": t,
            "active_page": "compare",
        },
    )

@router.get("/go/{partner_id}")
async def affiliate_redirect(
    partner_id: str,
    request: Request,
    country: str = "fi",
    category: str = "general",
    db: Session = Depends(get_session),
):
    """Outbound tracking redirect."""
    page_path = request.headers.get("referer", "/")
    target_url = record_affiliate_click(
        db=db,
        partner_id=partner_id,
        country_code=country,
        category=category,
        page_path=page_path,
    )
    return RedirectResponse(url=target_url or "/", status_code=307)

@router.get("/{country}/{lang}/privacy/", response_class=HTMLResponse)
async def privacy_policy(country: str, lang: str, request: Request):
    """GDPR Privacy policy page."""
    pack = country_registry.get(country)
    if not pack:
        raise HTTPException(status_code=404, detail="Country pack not found")

    all_packs = country_registry.get_all()
    t = get_translator(lang)
    privacy_info = pack.legal_info.get("privacy_notice", {})

    content = f"""
    <h3>1. Data Controller</h3>
    <p>{privacy_info.get('company_name', 'OmniFinance Platform')} ({privacy_info.get('contact_email', 'privacy@omnifinance.io')})</p>
    <h3>2. Data Processing Principles</h3>
    <p>{privacy_info.get('gdpr_statement', 'We do not collect or store individual calculator entries on our servers.')}</p>
    <h3>3. Cookies and Advertising</h3>
    <p>We use local storage strictly to remember your preferred UI theme and selected country. Third-party advertising partners such as Google AdSense may place cookies when you grant explicit consent.</p>
    """

    return templates.TemplateResponse(
        request=request,
        name="article.html",
        context={
            "all_countries": all_packs,
            "current_country_pack": pack,
            "country_code": pack.code,
            "lang": lang,
            "title": "Privacy Policy & GDPR Compliance",
            "content": content,
            "t": t,
        },
    )

@router.get("/{country}/{lang}/terms/", response_class=HTMLResponse)
async def terms_of_service(country: str, lang: str, request: Request):
    """Terms of service page."""
    pack = country_registry.get(country)
    if not pack:
        raise HTTPException(status_code=404, detail="Country pack not found")

    all_packs = country_registry.get_all()
    t = get_translator(lang)
    disclaimer = pack.legal_info.get("disclaimer", {}).get("text", "")

    content = f"""
    <h3>1. Informational Service Only</h3>
    <p>{disclaimer}</p>
    <h3>2. No Financial Advice</h3>
    <p>The calculations and AI-generated fiscal explanations are mathematical approximations and do not constitute certified tax advice. Users should consult their local tax office (e.g. Vero in Finland) before making financial decisions.</p>
    """

    return templates.TemplateResponse(
        request=request,
        name="article.html",
        context={
            "all_countries": all_packs,
            "current_country_pack": pack,
            "country_code": pack.code,
            "lang": lang,
            "title": "Terms of Service",
            "content": content,
            "t": t,
        },
    )

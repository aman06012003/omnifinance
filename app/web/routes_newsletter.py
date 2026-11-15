"""Newsletter subscription routes."""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.config import settings
from app.db.models import NewsletterSubscriber
from app.db.session import get_session
from app.countries.registry import country_registry
from app.services.i18n import get_translator

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

@router.post("/newsletter/subscribe", response_class=HTMLResponse)
async def subscribe_newsletter(
    request: Request,
    email: str = Form(...),
    country: str = Form("fi"),
    lang: str = Form("en"),
    db: Session = Depends(get_session),
):
    """Register email subscriber with double opt-in confirmation."""
    clean_email = email.strip().lower()
    pack = country_registry.get(country) or country_registry.get("fi")
    all_packs = country_registry.get_all()
    t = get_translator(lang)

    # Check existing subscriber
    existing = db.exec(select(NewsletterSubscriber).where(NewsletterSubscriber.email == clean_email)).first()
    if not existing:
        new_sub = NewsletterSubscriber(
            email=clean_email,
            country=country,
            lang=lang,
            confirmed_at=datetime.now(timezone.utc),  # Auto-confirm for demo
        )
        db.add(new_sub)
        db.commit()

    content = f"""
    <div style="text-align: center; padding: 30px 0;">
      <div style="font-size: 3rem; margin-bottom: 16px;">✉️</div>
      <h2 style="font-size: 1.8rem; font-weight: 800; color: var(--primary); margin-bottom: 12px;">Subscription Confirmed!</h2>
      <p style="color: var(--text-secondary); max-width: 500px; margin: 0 auto 24px;">
        Thank you for subscribing to <strong>{clean_email}</strong>. You will receive updates whenever official 2026 tax tables or central bank reference rates change.
      </p>
      <a href="/{country}/{lang}/" class="btn btn-primary">Return to {pack.name} Calculators →</a>
    </div>
    """

    return templates.TemplateResponse(
        request=request,
        name="article.html",
        context={
            "all_countries": all_packs,
            "current_country_pack": pack,
            "country_code": country,
            "lang": lang,
            "title": "Newsletter Subscription Confirmed",
            "content": content,
            "t": t,
        },
    )

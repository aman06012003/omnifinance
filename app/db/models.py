"""Database SQLModel entities."""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class NewsletterSubscriber(SQLModel, table=True):
    __tablename__ = "newsletter_subscribers"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False)
    country: str = Field(default="fi", max_length=10)
    lang: str = Field(default="en", max_length=10)
    confirmed_at: Optional[datetime] = Field(default=None)
    unsubscribed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now)

class AffiliateClick(SQLModel, table=True):
    __tablename__ = "affiliate_clicks"

    id: Optional[int] = Field(default=None, primary_key=True)
    partner_id: str = Field(index=True, nullable=False)
    category: str = Field(default="general", max_length=50)
    country: str = Field(default="fi", max_length=10)
    page_path: str = Field(default="/", max_length=255)
    created_at: datetime = Field(default_factory=get_utc_now)

class CalculatorEvent(SQLModel, table=True):
    __tablename__ = "calculator_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    calculator_id: str = Field(index=True, nullable=False)
    country: str = Field(default="fi", max_length=10)
    lang: str = Field(default="en", max_length=10)
    created_at: datetime = Field(default_factory=get_utc_now)

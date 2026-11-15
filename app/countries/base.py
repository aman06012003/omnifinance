"""Abstract base models and interfaces for Country Packs."""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class TaxBreakdownItem(BaseModel):
    name: str
    rate_percent: Decimal
    amount_annual: Decimal
    amount_monthly: Decimal
    category: str  # e.g., 'tax', 'social_security', 'pension'

class TaxResult(BaseModel):
    gross_annual: Decimal
    gross_monthly: Decimal
    net_annual: Decimal
    net_monthly: Decimal

    # Deduction components
    state_tax: Decimal = Decimal("0.00")
    municipal_tax: Decimal = Decimal("0.00")
    church_tax: Decimal = Decimal("0.00")
    pension_contribution: Decimal = Decimal("0.00")
    unemployment_insurance: Decimal = Decimal("0.00")
    health_insurance: Decimal = Decimal("0.00")
    total_deductions: Decimal = Decimal("0.00")

    # Rates
    effective_rate_percent: Decimal = Decimal("0.00")
    marginal_rate_percent: Decimal = Decimal("0.00")

    # Granular line items for transparent UI breakdown
    breakdown: List[TaxBreakdownItem] = Field(default_factory=list)
    currency: str = "EUR"
    currency_symbol: str = "€"
    tax_year: int = 2026
    notes: List[str] = Field(default_factory=list)

class Municipality(BaseModel):
    name: str
    code: Optional[str] = None
    tax_rate_percent: Decimal
    church_tax_rate_percent: Decimal = Decimal("1.00")

class CountryPackConfig(BaseModel):
    code: str
    name: str
    default_language: str = "en"
    languages: List[str] = Field(default_factory=lambda: ["en"])
    currency: str = "EUR"
    currency_symbol: str = "€"
    number_format: Dict[str, str] = Field(default_factory=lambda: {"decimal": ",", "thousands": " "})
    date_format: str = "%d.%m.%Y"
    domain_path: str = "/fi"
    enabled_calculators: List[str] = Field(default_factory=list)
    adsense_enabled: bool = True
    tax_year: int = 2026
    tax_source_urls: List[str] = Field(default_factory=list)

class AffiliatePartner(BaseModel):
    id: str
    name: str
    url: str
    category: str
    rating: float = 4.8
    headline: str = ""
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    featured: bool = False
    disclosure_required: bool = True

class TaxEngine(ABC):
    """Abstract Tax Engine interface that all country tax modules implement."""

    @abstractmethod
    def gross_to_net(
        self,
        gross_annual: Decimal,
        municipality: Optional[str] = None,
        is_church_member: bool = False,
        age: int = 30,
        **kwargs: Any
    ) -> TaxResult:
        """Calculate net salary and all tax & social deductions from annual gross."""
        pass

    @abstractmethod
    def get_municipalities(self) -> List[Municipality]:
        """Return list of supported municipalities and their tax rates."""
        pass

class CountryPack:
    """Encapsulates a loaded country pack."""

    def __init__(
        self,
        config: CountryPackConfig,
        tax_engine: Optional[TaxEngine] = None,
        calculators_config: Optional[Dict[str, Any]] = None,
        affiliates: Optional[List[AffiliatePartner]] = None,
        legal_info: Optional[Dict[str, Any]] = None,
    ):
        self.config = config
        self.tax_engine = tax_engine
        self.calculators_config = calculators_config or {}
        self.affiliates = affiliates or []
        self.legal_info = legal_info or {}

    @property
    def code(self) -> str:
        return self.config.code

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def currency_symbol(self) -> str:
        return self.config.currency_symbol

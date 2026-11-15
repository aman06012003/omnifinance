"""Template Tax Engine (flat tax example)."""
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Any

from app.countries.base import TaxEngine, TaxResult, TaxBreakdownItem, Municipality

class TemplateTaxEngine(TaxEngine):
    def __init__(self, pack_dir: Path) -> None:
        self.pack_dir = pack_dir

    def get_municipalities(self) -> List[Municipality]:
        return [Municipality(name="Standard Region", tax_rate_percent=Decimal("5.00"))]

    def gross_to_net(
        self,
        gross_annual: Decimal,
        municipality: Optional[str] = None,
        is_church_member: bool = False,
        age: int = 30,
        **kwargs: Any
    ) -> TaxResult:
        income_tax = gross_annual * Decimal("0.20")
        pension = gross_annual * Decimal("0.07")
        total_deductions = income_tax + pension
        net_annual = max(Decimal("0.00"), gross_annual - total_deductions)

        return TaxResult(
            gross_annual=gross_annual,
            gross_monthly=gross_annual / Decimal("12"),
            net_annual=net_annual,
            net_monthly=net_annual / Decimal("12"),
            state_tax=income_tax,
            pension_contribution=pension,
            total_deductions=total_deductions,
            effective_rate_percent=Decimal("27.00"),
            marginal_rate_percent=Decimal("27.00"),
            breakdown=[
                TaxBreakdownItem(
                    name="Income Tax",
                    rate_percent=Decimal("20.00"),
                    amount_annual=income_tax,
                    amount_monthly=income_tax / Decimal("12"),
                    category="tax",
                ),
                TaxBreakdownItem(
                    name="Pension Contribution",
                    rate_percent=Decimal("7.00"),
                    amount_annual=pension,
                    amount_monthly=pension / Decimal("12"),
                    category="pension",
                ),
            ],
            currency="EUR",
            currency_symbol="€",
            tax_year=2026,
            notes=["Template flat tax calculation."],
        )

Engine = TemplateTaxEngine

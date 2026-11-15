"""Finland Tax Engine (Vero 2026 Rules)."""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

from app.countries.base import TaxEngine, TaxResult, TaxBreakdownItem, Municipality

def to_dec(val: Any) -> Decimal:
    """Safe conversion to 2-decimal place Decimal."""
    if val is None:
        return Decimal("0.00")
    if isinstance(val, (int, str)):
        return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if isinstance(val, float):
        return Decimal(f"{val:.2f}").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal("0.00")

class FITaxEngine(TaxEngine):
    def __init__(self, pack_dir: Path) -> None:
        self.pack_dir = pack_dir
        self.tax_data_path = pack_dir / "tax_data_2026.yaml"
        self._load_tax_data()

    def _load_tax_data(self) -> None:
        with open(self.tax_data_path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

        self.tax_year = self.data.get("tax_year", 2026)
        self.social_data = self.data.get("social_security", {})
        self.brackets_data = self.data.get("state_income_tax_brackets", [])
        self.municipalities_data = self.data.get("municipalities", [])
        self.deductions_data = self.data.get("deductions", {})

    def get_municipalities(self) -> List[Municipality]:
        return [
            Municipality(
                name=m["name"],
                code=m.get("code"),
                tax_rate_percent=to_dec(m["tax_rate_percent"]),
                church_tax_rate_percent=to_dec(m.get("church_tax_rate_percent", 1.0)),
            )
            for m in self.municipalities_data
        ]

    def _get_municipality_rate(self, name: Optional[str]) -> tuple[Decimal, Decimal]:
        if not name:
            name = "Helsinki"
        for m in self.municipalities_data:
            if m["name"].lower() == name.lower():
                return to_dec(m["tax_rate_percent"]), to_dec(m.get("church_tax_rate_percent", 1.0))
        # Default to Average Finland rate
        return Decimal("7.40"), Decimal("1.10")

    def _calculate_state_tax(self, taxable_income: Decimal) -> tuple[Decimal, Decimal]:
        """Calculates state tax and marginal state rate."""
        if taxable_income <= 0:
            return Decimal("0.00"), Decimal("0.00")

        state_tax = Decimal("0.00")
        marginal_rate = Decimal("0.00")

        for b in self.brackets_data:
            lower = Decimal(str(b["lower"]))
            upper = Decimal(str(b["upper"])) if b.get("upper") is not None else None
            rate = Decimal(str(b["rate_percent"])) / Decimal("100")
            base_tax = Decimal(str(b["base_tax"]))

            if upper is not None:
                if lower < taxable_income <= upper:
                    excess = taxable_income - lower
                    state_tax = base_tax + (excess * rate)
                    marginal_rate = Decimal(str(b["rate_percent"]))
                    break
            else:
                if taxable_income > lower:
                    excess = taxable_income - lower
                    state_tax = base_tax + (excess * rate)
                    marginal_rate = Decimal(str(b["rate_percent"]))
                    break

        return to_dec(state_tax), marginal_rate

    def gross_to_net(
        self,
        gross_annual: Decimal,
        municipality: Optional[str] = "Helsinki",
        is_church_member: bool = False,
        age: int = 30,
        **kwargs: Any
    ) -> TaxResult:
        gross_annual = to_dec(gross_annual)
        if gross_annual <= 0:
            return TaxResult(
                gross_annual=Decimal("0.00"),
                gross_monthly=Decimal("0.00"),
                net_annual=Decimal("0.00"),
                net_monthly=Decimal("0.00"),
                currency="EUR",
                currency_symbol="€",
            )

        gross_monthly = to_dec(gross_annual / Decimal("12"))

        # 1. Social Insurance Contributions (Deductible from taxable income)
        # TyEL Pension (7.15% standard, 8.65% for ages 53-62)
        tyel_rate = Decimal(str(self.social_data.get("pension_tyel_senior", 8.65) if 53 <= age <= 62 else self.social_data.get("pension_tyel_standard", 7.15)))
        pension_contrib = to_dec(gross_annual * (tyel_rate / Decimal("100")))

        # Unemployment Insurance (0.79%)
        unemp_rate = Decimal(str(self.social_data.get("unemployment_insurance", 0.79)))
        unemp_contrib = to_dec(gross_annual * (unemp_rate / Decimal("100")))

        # Health Insurance (1.52% overall)
        health_rate = Decimal(str(self.social_data.get("health_insurance", 1.52)))
        health_threshold = Decimal(str(self.social_data.get("health_insurance_threshold", 16499)))
        health_contrib = to_dec(gross_annual * (health_rate / Decimal("100"))) if gross_annual > health_threshold else Decimal("0.00")

        # 2. Taxable Income for State & Municipal taxes
        # Under Finnish law, employee pension and unemployment insurance are deductible from gross income
        taxable_income = max(Decimal("0.00"), gross_annual - pension_contrib - unemp_contrib)

        # 3. State Progressive Tax
        state_tax, marginal_state_rate = self._calculate_state_tax(taxable_income)

        # 4. Municipal Tax
        muni_rate, church_rate = self._get_municipality_rate(municipality)
        municipal_tax = to_dec(taxable_income * (muni_rate / Decimal("100")))

        # 5. Church Tax (optional)
        church_tax = Decimal("0.00")
        if is_church_member:
            church_tax = to_dec(taxable_income * (church_rate / Decimal("100")))

        # 6. Work Income Tax Credit (Työtulovähennys)
        max_credit = Decimal(str(self.deductions_data.get("work_income_tax_credit_max", 2140)))
        threshold = Decimal(str(self.deductions_data.get("work_income_tax_credit_threshold", 22000)))
        reduction_rate = Decimal(str(self.deductions_data.get("work_income_reduction_rate", 0.05)))

        credit = max_credit
        if taxable_income > threshold:
            credit = max(Decimal("0.00"), max_credit - ((taxable_income - threshold) * reduction_rate))

        # Credit reduces state tax first, then municipal tax
        if credit > 0:
            if state_tax >= credit:
                state_tax = to_dec(state_tax - credit)
            else:
                remaining_credit = credit - state_tax
                state_tax = Decimal("0.00")
                municipal_tax = to_dec(max(Decimal("0.00"), municipal_tax - remaining_credit))

        # Total Deductions
        total_deductions = to_dec(
            state_tax + municipal_tax + church_tax + pension_contrib + unemp_contrib + health_contrib
        )

        net_annual = to_dec(max(Decimal("0.00"), gross_annual - total_deductions))
        net_monthly = to_dec(net_annual / Decimal("12"))

        effective_rate = to_dec((total_deductions / gross_annual) * Decimal("100")) if gross_annual > 0 else Decimal("0.00")
        total_marginal_rate = to_dec(marginal_state_rate + muni_rate + tyel_rate + unemp_rate + (church_rate if is_church_member else Decimal("0.00")))

        # Granular breakdown items
        breakdown: List[TaxBreakdownItem] = [
            TaxBreakdownItem(
                name="Municipal Tax (Kunnallisvero)",
                rate_percent=muni_rate,
                amount_annual=municipal_tax,
                amount_monthly=to_dec(municipal_tax / Decimal("12")),
                category="tax",
            ),
            TaxBreakdownItem(
                name="State Income Tax (Valtionvero)",
                rate_percent=marginal_state_rate,
                amount_annual=state_tax,
                amount_monthly=to_dec(state_tax / Decimal("12")),
                category="tax",
            ),
            TaxBreakdownItem(
                name="TyEL Pension Contribution (Eläkemaksu)",
                rate_percent=tyel_rate,
                amount_annual=pension_contrib,
                amount_monthly=to_dec(pension_contrib / Decimal("12")),
                category="pension",
            ),
            TaxBreakdownItem(
                name="Unemployment Insurance (Työttömyysvakuutus)",
                rate_percent=unemp_rate,
                amount_annual=unemp_contrib,
                amount_monthly=to_dec(unemp_contrib / Decimal("12")),
                category="social_security",
            ),
            TaxBreakdownItem(
                name="Health Insurance (Sairausvakuutus)",
                rate_percent=health_rate if health_contrib > 0 else Decimal("0.00"),
                amount_annual=health_contrib,
                amount_monthly=to_dec(health_contrib / Decimal("12")),
                category="social_security",
            ),
        ]

        if is_church_member:
            breakdown.append(
                TaxBreakdownItem(
                    name="Church Tax (Kirkollisvero)",
                    rate_percent=church_rate,
                    amount_annual=church_tax,
                    amount_monthly=to_dec(church_tax / Decimal("12")),
                    category="tax",
                )
            )

        notes = [
            f"Tax rates based on Vero.fi 2026 guidelines for {municipality}.",
            f"TyEL employee pension rate is {tyel_rate}%.",
            f"Employee unemployment insurance rate is {unemp_rate}%.",
        ]

        return TaxResult(
            gross_annual=gross_annual,
            gross_monthly=gross_monthly,
            net_annual=net_annual,
            net_monthly=net_monthly,
            state_tax=state_tax,
            municipal_tax=municipal_tax,
            church_tax=church_tax,
            pension_contribution=pension_contrib,
            unemployment_insurance=unemp_contrib,
            health_insurance=health_contrib,
            total_deductions=total_deductions,
            effective_rate_percent=effective_rate,
            marginal_rate_percent=total_marginal_rate,
            breakdown=breakdown,
            currency="EUR",
            currency_symbol="€",
            tax_year=self.tax_year,
            notes=notes,
        )

# Module export expected by CountryRegistry
Engine = FITaxEngine

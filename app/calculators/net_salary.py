"""Net Salary Calculator (integrates with country TaxEngine & SVG charts)."""
from decimal import Decimal
from typing import Any, Dict, List
from pydantic import Field

from app.calculators.base import Calculator, BaseCalculatorResult, round_curr, to_decimal
from app.countries.base import TaxResult
from app.charts.svg_charts import render_breakdown_donut

class NetSalaryResult(BaseCalculatorResult):
    gross_monthly: Decimal
    gross_annual: Decimal
    net_monthly: Decimal
    net_annual: Decimal
    total_deductions_monthly: Decimal
    total_deductions_annual: Decimal
    effective_tax_rate: Decimal
    marginal_tax_rate: Decimal
    municipality: str
    tax_result: TaxResult
    chart_slices: List[Dict[str, Any]] = Field(default_factory=list)

class NetSalaryCalculator(Calculator):
    id = "net_salary"
    name = "Net Salary Calculator"
    description = "Calculate your net take-home salary after state and municipal taxes and pension deductions."

    def calculate(self, inputs: Dict[str, Any], country_pack: Any) -> NetSalaryResult:
        raw_amount = inputs.get("amount", 3800)
        period = inputs.get("period", "month")
        municipality = inputs.get("municipality", "Helsinki")
        is_church = str(inputs.get("is_church_member", "false")).lower() in ("true", "1", "yes", "on")
        age = int(inputs.get("age", 30))

        gross_input = to_decimal(raw_amount)
        if period == "month":
            gross_annual = gross_input * Decimal("12")
        else:
            gross_annual = gross_input

        # Call country tax engine
        tax_engine = getattr(country_pack, "tax_engine", None)
        if tax_engine:
            tax_res: TaxResult = tax_engine.gross_to_net(
                gross_annual=gross_annual,
                municipality=municipality,
                is_church_member=is_church,
                age=age,
            )
        else:
            raise ValueError(f"No TaxEngine configured for country pack {country_pack.code}")

        # Prepare slices for SVG Donut
        chart_slices = [
            {"name": "Take-Home Pay", "value": tax_res.net_monthly, "color": "#10b981"},
            {"name": "Municipal Tax", "value": round_curr(tax_res.municipal_tax / Decimal("12")), "color": "#6366f1"},
            {"name": "State Tax", "value": round_curr(tax_res.state_tax / Decimal("12")), "color": "#f59e0b"},
            {"name": "TyEL Pension", "value": round_curr(tax_res.pension_contribution / Decimal("12")), "color": "#06b6d4"},
            {"name": "Unemployment Ins.", "value": round_curr(tax_res.unemployment_insurance / Decimal("12")), "color": "#ec4899"},
        ]
        if tax_res.health_insurance > 0:
            chart_slices.append({
                "name": "Health Ins.",
                "value": round_curr(tax_res.health_insurance / Decimal("12")),
                "color": "#8b5cf6",
            })
        if tax_res.church_tax > 0:
            chart_slices.append({
                "name": "Church Tax",
                "value": round_curr(tax_res.church_tax / Decimal("12")),
                "color": "#f43f5e",
            })

        svg_chart = render_breakdown_donut(
            slices=chart_slices,
            center_label="Net Take-Home",
            center_sublabel=f"{country_pack.currency_symbol}{tax_res.net_monthly:,.2f}",
        )

        return NetSalaryResult(
            calculator_id=self.id,
            country=country_pack.code,
            currency_symbol=country_pack.currency_symbol,
            gross_monthly=tax_res.gross_monthly,
            gross_annual=tax_res.gross_annual,
            net_monthly=tax_res.net_monthly,
            net_annual=tax_res.net_annual,
            total_deductions_monthly=round_curr(tax_res.total_deductions / Decimal("12")),
            total_deductions_annual=tax_res.total_deductions,
            effective_tax_rate=tax_res.effective_rate_percent,
            marginal_tax_rate=tax_res.marginal_rate_percent,
            municipality=municipality,
            tax_result=tax_res,
            chart_slices=chart_slices,
            svg_chart=svg_chart,
            assumptions={
                "Municipality": municipality,
                "Age": age,
                "Church member": "Yes" if is_church else "No",
                "Tax year": tax_res.tax_year,
            },
        )

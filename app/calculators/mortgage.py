"""Mortgage & Euribor Sensitivity Stress-Test Calculator."""
from decimal import Decimal
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from app.calculators.base import Calculator, BaseCalculatorResult, round_curr, to_decimal
from app.charts.svg_charts import render_breakdown_donut

class StressTestScenario(BaseModel):
    rate_percent: Decimal
    monthly_payment: Decimal
    difference_monthly: Decimal
    total_extra_interest: Decimal

class MortgageResult(BaseCalculatorResult):
    property_price: Decimal
    down_payment: Decimal
    loan_amount: Decimal
    ltv_percent: Decimal
    annual_rate_percent: Decimal
    term_years: int
    monthly_payment: Decimal
    total_interest: Decimal
    total_cost: Decimal
    stress_scenarios: List[StressTestScenario] = Field(default_factory=list)

class MortgageCalculator(Calculator):
    id = "mortgage"
    name = "Mortgage Calculator"
    description = "Calculate mortgage installments with Euribor reference rates and interest rate sensitivity stress tests."

    def _calc_annuity_payment(self, principal: Decimal, annual_rate_percent: Decimal, total_months: int) -> Decimal:
        if principal <= 0 or total_months <= 0:
            return Decimal("0.00")
        monthly_rate = (annual_rate_percent / Decimal("100")) / Decimal("12")
        if monthly_rate <= 0:
            return principal / Decimal(str(total_months))
        factor = (Decimal("1") + monthly_rate) ** total_months
        return principal * (monthly_rate * factor) / (factor - Decimal("1"))

    def calculate(self, inputs: Dict[str, Any], country_pack: Any) -> MortgageResult:
        price = to_decimal(inputs.get("property_price", 260000))
        down_payment = to_decimal(inputs.get("down_payment", 40000))
        rate_percent = to_decimal(inputs.get("rate", 3.65))
        term_years = int(inputs.get("term_years", 25))

        loan_amount = max(Decimal("0.00"), price - down_payment)
        ltv_percent = (loan_amount / price * Decimal("100")) if price > 0 else Decimal("0.00")
        total_months = term_years * 12

        base_monthly = round_curr(self._calc_annuity_payment(loan_amount, rate_percent, total_months))
        total_cost = round_curr(base_monthly * Decimal(str(total_months)))
        total_interest = round_curr(max(Decimal("0.00"), total_cost - loan_amount))

        # Stress test scenarios (+1.0% and +2.0% rate increase)
        stress_scenarios: List[StressTestScenario] = []
        for extra_rate in [Decimal("1.0"), Decimal("2.0")]:
            stressed_rate = rate_percent + extra_rate
            stressed_monthly = round_curr(self._calc_annuity_payment(loan_amount, stressed_rate, total_months))
            diff_monthly = stressed_monthly - base_monthly
            total_extra = round_curr(diff_monthly * Decimal(str(total_months)))
            stress_scenarios.append(
                StressTestScenario(
                    rate_percent=stressed_rate,
                    monthly_payment=stressed_monthly,
                    difference_monthly=diff_monthly,
                    total_extra_interest=total_extra,
                )
            )

        # SVG Donut Chart: Down payment vs Loan Principal vs Total Interest
        slices = [
            {"name": "Down Payment Equity", "value": down_payment, "color": "#10b981"},
            {"name": "Loan Principal", "value": loan_amount, "color": "#6366f1"},
            {"name": "Total Interest Over Term", "value": total_interest, "color": "#f59e0b"},
        ]
        svg_chart = render_breakdown_donut(
            slices=slices,
            center_label="Monthly Installment",
            center_sublabel=f"{country_pack.currency_symbol}{base_monthly:,.2f}",
        )

        return MortgageResult(
            calculator_id=self.id,
            country=country_pack.code,
            currency_symbol=country_pack.currency_symbol,
            property_price=round_curr(price),
            down_payment=round_curr(down_payment),
            loan_amount=round_curr(loan_amount),
            ltv_percent=round_curr(ltv_percent),
            annual_rate_percent=round_curr(rate_percent),
            term_years=term_years,
            monthly_payment=base_monthly,
            total_interest=total_interest,
            total_cost=total_cost,
            stress_scenarios=stress_scenarios,
            svg_chart=svg_chart,
            assumptions={
                "Loan-to-Value (LTV)": f"{ltv_percent:.1f}%",
                "Euribor Margin & Rate": f"{rate_percent}% p.a.",
                "Loan Term": f"{term_years} years ({total_months} months)",
            },
        )

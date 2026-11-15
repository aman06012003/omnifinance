"""Mortgage Affordability & Debt-to-Income (DTI) Regulatory Calculator."""
from decimal import Decimal
from typing import Any, Dict
from app.calculators.base import Calculator, BaseCalculatorResult, round_curr, to_decimal
from app.charts.svg_charts import render_breakdown_donut

class AffordabilityResult(BaseCalculatorResult):
    gross_monthly: Decimal
    other_debt_monthly: Decimal
    available_equity: Decimal
    dti_limit_percent: Decimal

    max_monthly_capacity: Decimal
    available_mortgage_payment: Decimal
    max_borrowing_capacity: Decimal
    max_property_purchase_price: Decimal
    stress_rate_percent: Decimal

class AffordabilityCalculator(Calculator):
    id = "affordability"
    name = "Mortgage Affordability Calculator"
    description = "Determine your maximum borrowing limit and home purchase budget under regulatory stress-test guidelines."

    def calculate(self, inputs: Dict[str, Any], country_pack: Any) -> AffordabilityResult:
        gross_monthly = to_decimal(inputs.get("gross_monthly", 4500))
        other_debt = to_decimal(inputs.get("other_loans_monthly", 200))
        equity = to_decimal(inputs.get("savings_equity", 35000))
        dti_ratio = to_decimal(inputs.get("max_dti_ratio", 0.40))
        stress_rate = to_decimal(inputs.get("stress_rate", 6.0))
        term_years = int(inputs.get("term_years", 25))

        # Max monthly debt payment allowed by Fin-FSA / European Banking Guidelines
        max_total_debt_payment = gross_monthly * dti_ratio
        available_mortgage_payment = max(Decimal("0.00"), max_total_debt_payment - other_debt)

        # Calculate max loan using the 6.0% stress test interest rate
        total_months = term_years * 12
        monthly_stress_rate = (stress_rate / Decimal("100")) / Decimal("12")

        if monthly_stress_rate > 0 and total_months > 0 and available_mortgage_payment > 0:
            factor = (Decimal("1") + monthly_stress_rate) ** total_months
            max_loan = available_mortgage_payment * (factor - Decimal("1")) / (monthly_stress_rate * factor)
        else:
            max_loan = Decimal("0.00")

        max_loan = round_curr(max_loan)
        max_property_price = round_curr(max_loan + equity)

        # SVG Donut Chart: Max Loan + Personal Savings Equity
        slices = [
            {"name": "Max Bank Mortgage", "value": max_loan, "color": "#10b981"},
            {"name": "Personal Cash Equity", "value": round_curr(equity), "color": "#6366f1"},
        ]
        svg_chart = render_breakdown_donut(
            slices=slices,
            center_label="Max Budget",
            center_sublabel=f"{country_pack.currency_symbol}{max_property_price:,.0f}",
        )

        return AffordabilityResult(
            calculator_id=self.id,
            country=country_pack.code,
            currency_symbol=country_pack.currency_symbol,
            gross_monthly=round_curr(gross_monthly),
            other_debt_monthly=round_curr(other_debt),
            available_equity=round_curr(equity),
            dti_limit_percent=round_curr(dti_ratio * Decimal("100")),
            max_monthly_capacity=round_curr(max_total_debt_payment),
            available_mortgage_payment=round_curr(available_mortgage_payment),
            max_borrowing_capacity=max_loan,
            max_property_purchase_price=max_property_price,
            stress_rate_percent=round_curr(stress_rate),
            svg_chart=svg_chart,
            assumptions={
                "Maximum Debt-to-Income (DTI)": f"{dti_ratio * 100:.0f}%",
                "Regulatory Stress Rate": f"{stress_rate}% p.a. over {term_years} years (Fin-FSA standard)",
            },
        )

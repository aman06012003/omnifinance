"""Mortgage & Loan Early Repayment Calculator."""
from decimal import Decimal
from typing import Any, Dict
from app.calculators.base import Calculator, BaseCalculatorResult, round_curr, to_decimal
from app.charts.svg_charts import render_breakdown_donut

class EarlyRepaymentResult(BaseCalculatorResult):
    remaining_balance: Decimal
    current_payment: Decimal
    extra_monthly: Decimal
    interest_rate_percent: Decimal

    original_months: int
    new_months: int
    months_saved: int
    years_saved: Decimal

    original_total_interest: Decimal
    new_total_interest: Decimal
    interest_saved: Decimal

class EarlyRepaymentCalculator(Calculator):
    id = "early_repayment"
    name = "Early Repayment Calculator"
    description = "Determine how extra monthly payments reduce your loan duration and save you thousands in interest charges."

    def calculate(self, inputs: Dict[str, Any], country_pack: Any) -> EarlyRepaymentResult:
        balance = to_decimal(inputs.get("remaining_balance", 180000))
        payment = to_decimal(inputs.get("current_payment", 950))
        rate_percent = to_decimal(inputs.get("interest_rate", 3.7))
        extra_monthly = to_decimal(inputs.get("extra_monthly", 150))

        monthly_rate = (rate_percent / Decimal("100")) / Decimal("12")

        # 1. Simulate Original Repayment
        orig_bal = balance
        orig_months = 0
        orig_interest = Decimal("0.00")
        max_limit = 1200  # 100 years guard

        while orig_bal > 0 and orig_months < max_limit:
            orig_months += 1
            i_month = orig_bal * monthly_rate
            p_month = min(orig_bal, payment - i_month)
            if p_month <= 0:
                break  # Payment doesn't cover interest
            orig_bal -= p_month
            orig_interest += i_month

        # 2. Simulate Accelerated Repayment
        new_bal = balance
        new_months = 0
        new_interest = Decimal("0.00")
        accelerated_payment = payment + extra_monthly

        while new_bal > 0 and new_months < max_limit:
            new_months += 1
            i_month = new_bal * monthly_rate
            p_month = min(new_bal, accelerated_payment - i_month)
            if p_month <= 0:
                break
            new_bal -= p_month
            new_interest += i_month

        months_saved = max(0, orig_months - new_months)
        years_saved = round_curr(Decimal(str(months_saved)) / Decimal("12"))
        interest_saved = round_curr(max(Decimal("0.00"), orig_interest - new_interest))

        # SVG Donut: New Interest vs Interest Saved
        slices = [
            {"name": "Remaining Interest to Pay", "value": round_curr(new_interest), "color": "#f59e0b"},
            {"name": "Interest Cash Saved", "value": interest_saved, "color": "#10b981"},
        ]
        svg_chart = render_breakdown_donut(
            slices=slices,
            center_label="Direct Interest Saved",
            center_sublabel=f"{country_pack.currency_symbol}{interest_saved:,.0f}",
        )

        return EarlyRepaymentResult(
            calculator_id=self.id,
            country=country_pack.code,
            currency_symbol=country_pack.currency_symbol,
            remaining_balance=round_curr(balance),
            current_payment=round_curr(payment),
            extra_monthly=round_curr(extra_monthly),
            interest_rate_percent=round_curr(rate_percent),
            original_months=orig_months,
            new_months=new_months,
            months_saved=months_saved,
            years_saved=years_saved,
            original_total_interest=round_curr(orig_interest),
            new_total_interest=round_curr(new_interest),
            interest_saved=interest_saved,
            svg_chart=svg_chart,
            assumptions={
                "Extra Payment Applied": f"{country_pack.currency_symbol}{extra_monthly}/mo continuously towards principal",
                "Interest Rate Constant": f"{rate_percent}% p.a.",
            },
        )

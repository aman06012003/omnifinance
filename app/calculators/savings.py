"""Savings & Compound Interest Calculator."""
from decimal import Decimal
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from app.calculators.base import Calculator, BaseCalculatorResult, round_curr, to_decimal
from app.charts.svg_charts import render_breakdown_donut

class SavingsMilestone(BaseModel):
    year: int
    total_contributed: Decimal
    interest_earned: Decimal
    future_value: Decimal

class SavingsResult(BaseCalculatorResult):
    initial_deposit: Decimal
    monthly_deposit: Decimal
    annual_rate_percent: Decimal
    years: int
    total_contributions: Decimal
    total_interest: Decimal
    future_value: Decimal
    real_purchasing_power: Decimal  # Inflation-adjusted (2% CPI benchmark)
    milestones: List[SavingsMilestone] = Field(default_factory=list)

class SavingsCalculator(Calculator):
    id = "savings"
    name = "Savings & Compound Interest Calculator"
    description = "Project the exponential growth of your investments and savings through the power of compounding."

    def calculate(self, inputs: Dict[str, Any], country_pack: Any) -> SavingsResult:
        initial = to_decimal(inputs.get("initial_deposit", 5000))
        monthly = to_decimal(inputs.get("monthly_deposit", 300))
        rate_percent = to_decimal(inputs.get("annual_rate", 7.0))
        years = int(inputs.get("years", 15))

        monthly_rate = (rate_percent / Decimal("100")) / Decimal("12")
        total_months = years * 12

        balance = initial
        total_contributions = initial
        milestones: List[SavingsMilestone] = []

        for m in range(1, total_months + 1):
            interest = balance * monthly_rate
            balance += interest + monthly
            total_contributions += monthly

            if m % 12 == 0 or m == total_months:
                yr = m // 12
                milestones.append(
                    SavingsMilestone(
                        year=yr,
                        total_contributed=round_curr(total_contributions),
                        interest_earned=round_curr(balance - total_contributions),
                        future_value=round_curr(balance),
                    )
                )

        total_interest = round_curr(max(Decimal("0.00"), balance - total_contributions))
        future_val = round_curr(balance)

        # 2% standard inflation deflator for purchasing power comparison
        inflation_rate = Decimal("0.02")
        deflator = (Decimal("1") + inflation_rate) ** years
        real_value = round_curr(future_val / deflator)

        # SVG Donut Chart: Contributions vs Compound Growth
        slices = [
            {"name": "Total Deposits", "value": round_curr(total_contributions), "color": "#6366f1"},
            {"name": "Compound Interest", "value": total_interest, "color": "#10b981"},
        ]
        svg_chart = render_breakdown_donut(
            slices=slices,
            center_label="Future Portfolio",
            center_sublabel=f"{country_pack.currency_symbol}{future_val:,.0f}",
        )

        return SavingsResult(
            calculator_id=self.id,
            country=country_pack.code,
            currency_symbol=country_pack.currency_symbol,
            initial_deposit=round_curr(initial),
            monthly_deposit=round_curr(monthly),
            annual_rate_percent=round_curr(rate_percent),
            years=years,
            total_contributions=round_curr(total_contributions),
            total_interest=total_interest,
            future_value=future_val,
            real_purchasing_power=real_value,
            milestones=milestones,
            svg_chart=svg_chart,
            assumptions={
                "Compounding Frequency": "Monthly",
                "Assumed Annual Return": f"{rate_percent}%",
                "Inflation Benchmark": "2.0% annual CPI erosion model",
            },
        )

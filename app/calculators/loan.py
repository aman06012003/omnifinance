"""Loan Payment & Amortization Calculator."""
from decimal import Decimal
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from app.calculators.base import Calculator, BaseCalculatorResult, round_curr, to_decimal
from app.charts.svg_charts import render_amortization_chart, render_breakdown_donut

class AmortizationRow(BaseModel):
    year: int
    month: int
    payment: Decimal
    principal_paid: Decimal
    interest_paid: Decimal
    total_interest: Decimal
    remaining_balance: Decimal

class LoanResult(BaseCalculatorResult):
    principal: Decimal
    annual_rate_percent: Decimal
    term_years: int
    monthly_payment: Decimal
    total_interest: Decimal
    total_cost: Decimal
    schedule_sample: List[AmortizationRow] = Field(default_factory=list)

class LoanCalculator(Calculator):
    id = "loan"
    name = "Loan Calculator"
    description = "Calculate monthly payments, total interest, and full repayment amortization schedule."

    def calculate(self, inputs: Dict[str, Any], country_pack: Any) -> LoanResult:
        principal = to_decimal(inputs.get("amount", 15000))
        rate_percent = to_decimal(inputs.get("rate", 6.9))
        term_years = int(inputs.get("term_years", 5))
        repayment_type = inputs.get("repayment_type", "annuity")

        total_months = term_years * 12
        if total_months <= 0 or principal <= 0:
            return LoanResult(
                calculator_id=self.id,
                country=country_pack.code,
                currency_symbol=country_pack.currency_symbol,
                principal=principal,
                annual_rate_percent=rate_percent,
                term_years=term_years,
                monthly_payment=Decimal("0.00"),
                total_interest=Decimal("0.00"),
                total_cost=Decimal("0.00"),
            )

        monthly_rate = (rate_percent / Decimal("100")) / Decimal("12")

        balance = principal
        total_interest = Decimal("0.00")
        schedule: List[AmortizationRow] = []
        chart_points: List[Dict[str, Any]] = []

        if repayment_type == "equal_principal":
            fixed_principal_payment = principal / Decimal(str(total_months))
            first_month_payment = Decimal("0.00")

            for m in range(1, total_months + 1):
                interest_month = balance * monthly_rate
                payment_month = fixed_principal_payment + interest_month
                balance = max(Decimal("0.00"), balance - fixed_principal_payment)
                total_interest += interest_month

                if m == 1:
                    first_month_payment = payment_month

                # Sample annually or last month
                if m % 12 == 0 or m == total_months:
                    schedule.append(
                        AmortizationRow(
                            year=m // 12,
                            month=m,
                            payment=round_curr(payment_month),
                            principal_paid=round_curr(fixed_principal_payment * Decimal(str(min(m, 12)))),
                            interest_paid=round_curr(interest_month),
                            total_interest=round_curr(total_interest),
                            remaining_balance=round_curr(balance),
                        )
                    )
                    chart_points.append({
                        "year": m // 12,
                        "balance": float(balance),
                        "total_interest": float(total_interest),
                    })

            monthly_payment = round_curr(first_month_payment)
        else:
            # Standard Annuity
            if monthly_rate > 0:
                factor = (Decimal("1") + monthly_rate) ** total_months
                monthly_payment = principal * (monthly_rate * factor) / (factor - Decimal("1"))
            else:
                monthly_payment = principal / Decimal(str(total_months))

            monthly_payment = round_curr(monthly_payment)

            for m in range(1, total_months + 1):
                interest_month = balance * monthly_rate
                principal_month = min(balance, monthly_payment - interest_month)
                balance = max(Decimal("0.00"), balance - principal_month)
                total_interest += interest_month

                if m % 12 == 0 or m == total_months:
                    schedule.append(
                        AmortizationRow(
                            year=m // 12,
                            month=m,
                            payment=monthly_payment,
                            principal_paid=round_curr(principal_month),
                            interest_paid=round_curr(interest_month),
                            total_interest=round_curr(total_interest),
                            remaining_balance=round_curr(balance),
                        )
                    )
                    chart_points.append({
                        "year": m // 12,
                        "balance": float(balance),
                        "total_interest": float(total_interest),
                    })

        total_interest = round_curr(total_interest)
        total_cost = round_curr(principal + total_interest)

        # SVG Chart: Amortization curve
        svg_chart = render_amortization_chart(
            schedule=chart_points,
            currency_symbol=country_pack.currency_symbol,
        )

        return LoanResult(
            calculator_id=self.id,
            country=country_pack.code,
            currency_symbol=country_pack.currency_symbol,
            principal=round_curr(principal),
            annual_rate_percent=round_curr(rate_percent),
            term_years=term_years,
            monthly_payment=monthly_payment,
            total_interest=total_interest,
            total_cost=total_cost,
            schedule_sample=schedule,
            svg_chart=svg_chart,
            assumptions={
                "Repayment Type": "Annuity (Equal monthly payments)" if repayment_type == "annuity" else "Equal Principal Amortization",
                "Interest Rate": f"{rate_percent}% p.a.",
                "Term": f"{term_years} years ({total_months} months)",
            },
        )

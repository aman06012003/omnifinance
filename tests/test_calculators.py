"""Unit and property tests for generic calculators."""
from decimal import Decimal
import pytest

from app.calculators.loan import LoanCalculator
from app.calculators.mortgage import MortgageCalculator
from app.calculators.savings import SavingsCalculator
from app.calculators.early_repayment import EarlyRepaymentCalculator
from app.calculators.affordability import AffordabilityCalculator
from app.countries.base import CountryPack, CountryPackConfig

@pytest.fixture
def dummy_pack():
    config = CountryPackConfig(code="fi", name="Finland", currency="EUR", currency_symbol="€")
    return CountryPack(config=config)

def test_loan_calculator_annuity(dummy_pack):
    calc = LoanCalculator()
    inputs = {
        "amount": 10000,
        "rate": 5.0,
        "term_years": 3,
        "repayment_type": "annuity",
    }
    res = calc.calculate(inputs, dummy_pack)

    assert res.monthly_payment > 0
    assert res.total_cost > res.principal
    assert res.total_interest == res.total_cost - res.principal
    assert len(res.schedule_sample) > 0

def test_mortgage_stress_scenarios(dummy_pack):
    calc = MortgageCalculator()
    inputs = {
        "property_price": 300000,
        "down_payment": 50000,
        "rate": 3.5,
        "term_years": 25,
    }
    res = calc.calculate(inputs, dummy_pack)

    assert res.loan_amount == Decimal("250000.00")
    assert res.monthly_payment > 0
    assert len(res.stress_scenarios) == 2
    # Stress test payments must be higher than base payment
    assert res.stress_scenarios[0].monthly_payment > res.monthly_payment
    assert res.stress_scenarios[1].monthly_payment > res.stress_scenarios[0].monthly_payment

def test_savings_compound_growth(dummy_pack):
    calc = SavingsCalculator()
    inputs = {
        "initial_deposit": 5000,
        "monthly_deposit": 200,
        "annual_rate": 6.0,
        "years": 10,
    }
    res = calc.calculate(inputs, dummy_pack)

    assert res.future_value > res.total_contributions
    assert res.total_interest > 0
    assert res.real_purchasing_power < res.future_value  # Inflation erosion

def test_early_repayment_savings(dummy_pack):
    calc = EarlyRepaymentCalculator()
    inputs = {
        "remaining_balance": 150000,
        "current_payment": 850,
        "interest_rate": 3.5,
        "extra_monthly": 150,
    }
    res = calc.calculate(inputs, dummy_pack)

    assert res.interest_saved > 0
    assert res.months_saved > 0
    assert res.new_months < res.original_months

def test_affordability_limits(dummy_pack):
    calc = AffordabilityCalculator()
    inputs = {
        "gross_monthly": 4000,
        "other_loans_monthly": 200,
        "savings_equity": 30000,
        "max_dti_ratio": 0.40,
    }
    res = calc.calculate(inputs, dummy_pack)

    assert res.max_borrowing_capacity > 0
    assert res.max_property_purchase_price == res.max_borrowing_capacity + Decimal("30000.00")

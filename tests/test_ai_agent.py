"""Tests for Groq AI Tax Agent and Pydantic schemas."""
from decimal import Decimal
import pytest

from app.ai.schemas import (
    CountryTaxLawExtraction,
    TaxExplanationResponse,
    TaxBracketStructured,
)
from app.ai.tax_agent import groq_tax_agent

@pytest.mark.asyncio
async def test_ai_tax_explanation_schema_and_fallback():
    tax_result_summary = {
        "net_monthly": Decimal("2850.00"),
        "total_deductions": Decimal("950.00"),
        "effective_rate_percent": Decimal("25.0"),
        "state_tax": Decimal("250.00"),
        "municipal_tax": Decimal("310.00"),
        "pension_contribution": Decimal("270.00"),
        "unemployment_insurance": Decimal("30.00"),
    }

    explanation: TaxExplanationResponse = await groq_tax_agent.explain_tax_calculation(
        country="fi",
        gross_monthly=Decimal("3800.00"),
        municipality="Helsinki",
        tax_result=tax_result_summary,
    )

    assert isinstance(explanation, TaxExplanationResponse)
    assert len(explanation.headline) > 5
    assert len(explanation.key_takeaways) >= 3
    assert len(explanation.optimization_tips) >= 2
    assert explanation.confidence_score >= 0.90

@pytest.mark.asyncio
async def test_country_tax_law_extraction_schema():
    extraction: CountryTaxLawExtraction = await groq_tax_agent.extract_country_tax_laws("Finland", 2026)

    assert isinstance(extraction, CountryTaxLawExtraction)
    assert extraction.country_code == "fi"
    assert extraction.tax_year == 2026
    assert len(extraction.brackets) >= 4
    assert extraction.social_security.pension_employee_percent > 0

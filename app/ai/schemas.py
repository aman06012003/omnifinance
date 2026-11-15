"""Pydantic schemas for Groq LLM structured outputs via LangChain."""
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

class TaxBracketStructured(BaseModel):
    lower_bound: Decimal = Field(description="Lower income threshold for this tax bracket in EUR")
    upper_bound: Optional[Decimal] = Field(default=None, description="Upper income threshold in EUR or null if top bracket")
    base_tax: Decimal = Field(default=Decimal("0.0"), description="Fixed base tax amount on the lower threshold in EUR")
    rate_percent: Decimal = Field(description="Marginal tax percentage applied to income exceeding lower bound")

class TaxDeductionStructured(BaseModel):
    name: str = Field(description="Official name of the deduction or tax credit")
    max_amount: Optional[Decimal] = Field(default=None, description="Maximum deduction amount in EUR")
    description: str = Field(description="Summary of criteria and calculation mechanism")
    is_refundable: bool = Field(default=False, description="Whether this is a direct credit against tax or deduction from income")

class SocialSecurityRatesStructured(BaseModel):
    pension_employee_percent: Decimal = Field(description="Standard employee pension contribution percentage (e.g., TyEL in Finland)")
    unemployment_employee_percent: Decimal = Field(description="Employee unemployment insurance percentage")
    health_insurance_percent: Decimal = Field(description="Health & medical insurance contribution percentage")

class CountryTaxLawExtraction(BaseModel):
    country_code: str = Field(description="ISO 3166-1 alpha-2 country code (e.g. fi, se, de)")
    country_name: str = Field(description="Full English country name")
    tax_year: int = Field(description="Applicable tax year, e.g. 2026")
    brackets: List[TaxBracketStructured] = Field(description="Progressive national/state income tax brackets")
    social_security: SocialSecurityRatesStructured = Field(description="Standard statutory employee contributions")
    deductions: List[TaxDeductionStructured] = Field(default_factory=list, description="Key standard deductions and tax credits")
    municipal_tax_summary: str = Field(description="How local or municipal income tax is structured and typical rates")
    summary: str = Field(description="High-level executive summary of this country's earned income tax system")
    source_citations: List[str] = Field(default_factory=list, description="Official government or tax administration source URLs")

class TaxExplanationRequest(BaseModel):
    country: str = "fi"
    gross_monthly: Decimal
    municipality: str = "Helsinki"
    effective_rate_percent: Decimal
    net_monthly: Decimal
    user_question: Optional[str] = None

class TaxOptimizationTip(BaseModel):
    title: str = Field(description="Actionable title for the tax tip")
    description: str = Field(description="Clear explanation of how to apply or claim this deduction")
    estimated_impact: str = Field(description="Estimated financial saving or benefit")

class TaxExplanationResponse(BaseModel):
    headline: str = Field(description="Engaging, punchy summary of the tax outcome")
    detailed_explanation: str = Field(description="Clear breakdown of where every euro goes and why")
    key_takeaways: List[str] = Field(description="3 to 4 bullet points highlighting critical numbers")
    optimization_tips: List[TaxOptimizationTip] = Field(default_factory=list, description="Legitimate tax reduction tips (e.g. commuter deduction, remote work deduction)")
    confidence_score: float = Field(default=0.98, description="Model confidence in accuracy")
    legal_disclaimer: str = Field(default="This AI explanation is informational and does not constitute certified legal or tax advice.")

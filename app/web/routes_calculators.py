"""Financial Calculator web routes and Groq LLM tax analysis endpoints."""
from decimal import Decimal
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.countries.registry import country_registry
from app.services.i18n import get_translator
from app.ai.tax_agent import groq_tax_agent
from app.ai.schemas import TaxExplanationRequest, TaxExplanationResponse
from app.calculators.net_salary import NetSalaryCalculator
from app.calculators.loan import LoanCalculator
from app.calculators.mortgage import MortgageCalculator
from app.calculators.savings import SavingsCalculator
from app.calculators.early_repayment import EarlyRepaymentCalculator
from app.calculators.affordability import AffordabilityCalculator

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

CALCULATOR_REGISTRY = {
    "net_salary": NetSalaryCalculator(),
    "loan": LoanCalculator(),
    "mortgage": MortgageCalculator(),
    "savings": SavingsCalculator(),
    "early_repayment": EarlyRepaymentCalculator(),
    "affordability": AffordabilityCalculator(),
}

@router.get("/{country}/{lang}/{calculator_slug}/", response_class=HTMLResponse)
async def view_calculator(
    country: str,
    lang: str,
    calculator_slug: str,
    request: Request,
):
    """Render financial calculator with GET parameter results."""
    pack = country_registry.get(country)
    if not pack:
        raise HTTPException(status_code=404, detail="Country pack not found")

    calc_instance = CALCULATOR_REGISTRY.get(calculator_slug)
    if not calc_instance:
        raise HTTPException(status_code=404, detail="Calculator not found")

    all_packs = country_registry.get_all()
    t = get_translator(lang)
    calc_meta = pack.calculators_config.get(calculator_slug, {
        "title": calc_instance.name,
        "description": calc_instance.description,
    })

    # Query parameters
    inputs = dict(request.query_params)
    municipalities = pack.tax_engine.get_municipalities() if pack.tax_engine else []

    # If no parameters provided, populate defaults from pack config
    if not inputs:
        if calculator_slug == "net_salary":
            inputs["amount"] = pack.calculators_config.get("net_salary", {}).get("default_amount", 3800)
            inputs["period"] = "month"
            inputs["municipality"] = "Helsinki"
            inputs["age"] = 30
        elif calculator_slug == "loan":
            inputs["amount"] = pack.calculators_config.get("loan", {}).get("default_amount", 15000)
            inputs["rate"] = pack.calculators_config.get("loan", {}).get("default_rate", 6.9)
            inputs["term_years"] = pack.calculators_config.get("loan", {}).get("default_term_years", 5)
        elif calculator_slug == "mortgage":
            inputs["property_price"] = pack.calculators_config.get("mortgage", {}).get("default_property_price", 260000)
            inputs["down_payment"] = pack.calculators_config.get("mortgage", {}).get("default_down_payment", 40000)
            inputs["rate"] = pack.calculators_config.get("mortgage", {}).get("default_rate", 3.65)
            inputs["term_years"] = pack.calculators_config.get("mortgage", {}).get("default_term_years", 25)
        elif calculator_slug == "savings":
            inputs["initial_deposit"] = pack.calculators_config.get("savings", {}).get("default_initial_deposit", 5000)
            inputs["monthly_deposit"] = pack.calculators_config.get("savings", {}).get("default_monthly_deposit", 300)
            inputs["annual_rate"] = pack.calculators_config.get("savings", {}).get("default_annual_rate", 7.0)
            inputs["years"] = pack.calculators_config.get("savings", {}).get("default_years", 15)
        elif calculator_slug == "early_repayment":
            inputs["remaining_balance"] = pack.calculators_config.get("early_repayment", {}).get("default_remaining_balance", 180000)
            inputs["current_payment"] = pack.calculators_config.get("early_repayment", {}).get("default_current_payment", 950)
            inputs["interest_rate"] = pack.calculators_config.get("early_repayment", {}).get("default_interest_rate", 3.7)
            inputs["extra_monthly"] = pack.calculators_config.get("early_repayment", {}).get("default_extra_monthly", 150)
        elif calculator_slug == "affordability":
            inputs["gross_monthly"] = pack.calculators_config.get("affordability", {}).get("default_gross_monthly", 4500)
            inputs["other_loans_monthly"] = pack.calculators_config.get("affordability", {}).get("default_other_loans_monthly", 200)
            inputs["savings_equity"] = pack.calculators_config.get("affordability", {}).get("default_savings_equity", 35000)

    # Perform calculation
    result = None
    ai_tax_insight = None
    user_ai_query = inputs.get("ai_query", None)

    try:
        result = calc_instance.calculate(inputs, pack)

        # If net_salary, generate Groq LLM Tax Law Analysis
        if calculator_slug == "net_salary" and result:
            ai_tax_insight = await groq_tax_agent.explain_tax_calculation(
                country=country,
                gross_monthly=result.gross_monthly,
                municipality=inputs.get("municipality", "Helsinki"),
                tax_result={
                    "net_monthly": result.net_monthly,
                    "total_deductions": result.total_deductions_monthly,
                    "effective_rate_percent": result.effective_tax_rate,
                    "state_tax": result.tax_result.state_tax,
                    "municipal_tax": result.tax_result.municipal_tax,
                    "pension_contribution": result.tax_result.pension_contribution,
                    "unemployment_insurance": result.tax_result.unemployment_insurance,
                },
                user_question=user_ai_query,
            )
    except Exception as e:
        # Graceful handling
        result = None

    return templates.TemplateResponse(
        request=request,
        name="calculator.html",
        context={
            "all_countries": all_packs,
            "current_country_pack": pack,
            "country_code": pack.code,
            "lang": lang,
            "calc_id": calculator_slug,
            "calc_meta": calc_meta,
            "inputs": inputs,
            "result": result,
            "municipalities": municipalities,
            "ai_tax_insight": ai_tax_insight,
            "user_query": user_ai_query,
            "t": t,
            "active_page": calculator_slug,
        },
    )

@router.get("/{country}/{lang}/salary/{amount}/", response_class=HTMLResponse)
async def programmatic_salary_page(
    country: str,
    lang: str,
    amount: int,
    request: Request,
):
    """Programmatic SEO landing page for net salary on specific gross amounts."""
    pack = country_registry.get(country)
    if not pack:
        raise HTTPException(status_code=404, detail="Country pack not found")

    calc = CALCULATOR_REGISTRY["net_salary"]
    inputs = {
        "amount": amount,
        "period": "month",
        "municipality": "Helsinki",
        "age": 30,
    }
    result = calc.calculate(inputs, pack)
    all_packs = country_registry.get_all()
    t = get_translator(lang)

    ai_tax_insight = await groq_tax_agent.explain_tax_calculation(
        country=country,
        gross_monthly=Decimal(str(amount)),
        municipality="Helsinki",
        tax_result={
            "net_monthly": result.net_monthly,
            "total_deductions": result.total_deductions_monthly,
            "effective_rate_percent": result.effective_tax_rate,
            "state_tax": result.tax_result.state_tax,
            "municipal_tax": result.tax_result.municipal_tax,
            "pension_contribution": result.tax_result.pension_contribution,
            "unemployment_insurance": result.tax_result.unemployment_insurance,
        },
    )

    calc_meta = {
        "title": f"Net Salary on €{amount:,} / Month in {pack.name} (2026)",
        "description": f"Calculate take-home pay, state tax, and municipal deductions for an annual gross income of €{amount*12:,} in {pack.name}.",
    }

    return templates.TemplateResponse(
        request=request,
        name="calculator.html",
        context={
            "all_countries": all_packs,
            "current_country_pack": pack,
            "country_code": pack.code,
            "lang": lang,
            "calc_id": "net_salary",
            "calc_meta": calc_meta,
            "inputs": inputs,
            "result": result,
            "municipalities": pack.tax_engine.get_municipalities() if pack.tax_engine else [],
            "ai_tax_insight": ai_tax_insight,
            "t": t,
            "active_page": "net_salary",
        },
    )

@router.post("/api/ai/tax-explain", response_model=TaxExplanationResponse)
async def api_tax_explain(payload: TaxExplanationRequest):
    """JSON API endpoint for Groq LLaMA 3.1 structured tax explanation."""
    tax_result_summary = {
        "net_monthly": payload.net_monthly,
        "effective_rate_percent": payload.effective_rate_percent,
        "total_deductions": payload.gross_monthly - payload.net_monthly,
    }
    response = await groq_tax_agent.explain_tax_calculation(
        country=payload.country,
        gross_monthly=payload.gross_monthly,
        municipality=payload.municipality,
        tax_result=tax_result_summary,
        user_question=payload.user_question,
    )
    return response

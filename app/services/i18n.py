"""Internationalization (i18n) and localization service."""
from decimal import Decimal
from typing import Any, Dict

MESSAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "nav_calculators": "Calculators",
        "nav_compare": "Compare Offers",
        "nav_guides": "Guides",
        "nav_ai_tax": "Groq AI Tax Law",
        "select_country": "Country",
        "select_language": "Language",
        "btn_calculate": "Calculate Now",
        "btn_ask_ai": "Ask Groq AI Tax Law",
        "hero_title": "Smart Multi-Country Financial Intelligence",
        "hero_subtitle": "Precise tax engines, mortgage simulations, and AI-powered fiscal optimization across Nordic & European markets.",
        "disclaimer_short": "For informational purposes only. Not financial or tax advice.",
        "footer_rights": "All rights reserved. OmniFinance Platform.",
        "net_salary_title": "Net Salary After Tax",
        "loan_title": "Personal Loan Calculator",
        "mortgage_title": "Mortgage & Euribor Stress-Test",
        "savings_title": "Compound Interest & Growth",
        "early_repayment_title": "Early Repayment Savings",
        "affordability_title": "Mortgage Affordability",
        "monthly": "Monthly",
        "annual": "Annual",
        "gross_salary": "Gross Salary",
        "municipality": "Municipality",
        "church_tax": "Church Member",
        "age": "Age",
        "effective_rate": "Effective Tax Rate",
        "marginal_rate": "Marginal Tax Rate",
        "total_deductions": "Total Deductions",
        "take_home_pay": "Take-Home Pay",
        "ai_tax_insight": "AI Tax Law Intelligence (Groq LLaMA 3.1)",
        "compare_brokers": "Compare Brokers",
        "compare_mortgages": "Compare Mortgages",
        "compare_loans": "Compare Personal Loans",
    },
    "fi": {
        "nav_calculators": "Laskurit",
        "nav_compare": "Vertaile",
        "nav_guides": "Oppaat",
        "nav_ai_tax": "Tekoäly Veroanalyysi",
        "select_country": "Maa",
        "select_language": "Kieli",
        "btn_calculate": "Laske tulos",
        "btn_ask_ai": "Kysy Groq AI -veroasiantuntijalta",
        "hero_title": "Tarkka Talous- ja Verolaskurialusta",
        "hero_subtitle": "Reaaliaikaiset verolaskelmat, asuntolainan korkotestit ja LLaMA 3.1 -tekoälyn vero-optimointi.",
        "disclaimer_short": "Tiedot ovat suuntaa-antavia, eivätkä korvaa virallista vero- tai sijoitusneuvontaa.",
        "footer_rights": "Kaikki oikeudet pidätetään. OmniFinance Suomi.",
        "net_salary_title": "Palkkalaskuri (Nettoansio)",
        "loan_title": "Lainalaskuri",
        "mortgage_title": "Asuntolainalaskuri ja Korkotesti",
        "savings_title": "Korkoa korolle -laskuri",
        "early_repayment_title": "Lainan ennenaikainen takaisinmaksu",
        "affordability_title": "Lainalaskurin enimmäismäärä",
        "monthly": "Kuukausi",
        "annual": "Vuosi",
        "gross_salary": "Bruttopalkka",
        "municipality": "Kotikunta",
        "church_tax": "Kirkollisvero",
        "age": "Ikä",
        "effective_rate": "Efektiivinen veroaste",
        "marginal_rate": "Marginaalivero",
        "total_deductions": "Vähennykset yhteensä",
        "take_home_pay": "Käteenjäävä osuus",
        "ai_tax_insight": "Tekoälyn veroanalyysi (Groq LLaMA 3.1)",
        "compare_brokers": "Vertaile osakevälittäjiä",
        "compare_mortgages": "Vertaile asuntolainoja",
        "compare_loans": "Kilpailuta lainat",
    },
    "sv": {
        "nav_calculators": "Kalkyler",
        "nav_compare": "Jämför",
        "nav_guides": "Guider",
        "nav_ai_tax": "AI Skatteanalys",
        "select_country": "Land",
        "select_language": "Språk",
        "btn_calculate": "Beräkna",
        "btn_ask_ai": "Fråga Groq AI Skatteexpert",
        "hero_title": "Smart Finanskalkylator och Skatteplattform",
        "hero_subtitle": "Exakta skatteberäkningar, bolånestresstester och AI-driven skatteoptimering.",
        "disclaimer_short": "Endast i informationssyfte. Inte officiell finansiell eller skatterådgivning.",
        "footer_rights": "Alla rättigheter förbehållna. OmniFinance.",
        "net_salary_title": "Nettolön efter skatt",
        "loan_title": "Lånekalkylator",
        "mortgage_title": "Bolånekalkylator & Euribor",
        "savings_title": "Ränta på ränta kalkylator",
        "early_repayment_title": "Förtida återbetalning",
        "affordability_title": "Låneutrymme kalkylator",
        "monthly": "Månad",
        "annual": "År",
        "gross_salary": "Bruttolön",
        "municipality": "Hemkommun",
        "church_tax": "Kyrkoskatt",
        "age": "Ålder",
        "effective_rate": "Effektiv skattesats",
        "marginal_rate": "Marginalskatt",
        "total_deductions": "Totala avdrag",
        "take_home_pay": "Netto i plånboken",
        "ai_tax_insight": "AI Skatteinsikt (Groq LLaMA 3.1)",
        "compare_brokers": "Jämför nätmäklare",
        "compare_mortgages": "Jämför bolån",
        "compare_loans": "Jämför privatlån",
    },
}

class Translator:
    def __init__(self, lang: str = "en") -> None:
        self.lang = lang.lower() if lang.lower() in MESSAGES else "en"

    def get(self, key: str, default: str = "") -> str:
        return MESSAGES.get(self.lang, {}).get(key, MESSAGES["en"].get(key, default or key))

def get_translator(lang: str = "en") -> Translator:
    return Translator(lang)

def format_currency(amount: Any, symbol: str = "€", decimal_sep: str = ",", thousand_sep: str = " ") -> str:
    """Format decimal currency string based on country number format."""
    try:
        val = Decimal(str(amount))
        formatted = f"{val:,.2f}"
        # standard python format uses ',' for thousands and '.' for decimal
        parts = formatted.split(".")
        int_part = parts[0].replace(",", thousand_sep)
        dec_part = parts[1]
        return f"{int_part}{decimal_sep}{dec_part} {symbol}"
    except Exception:
        return f"{amount} {symbol}"

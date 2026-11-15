# OmniFinance: Multi-Country Finance Platform 🌍 🇫🇮

> **A high-performance, modular multi-country financial calculator platform and fiscal intelligence engine built with pure Python (FastAPI, Jinja2, SQLModel, Pydantic) and Groq LLaMA 3.1.**

---

## 📌 Project Overview & Utility

### The Problem It Solves
Managing personal finances, calculating net salary, and planning mortgages across international borders is notoriously complex. European and Nordic countries each feature unique, multi-tiered fiscal regimes:
- Progressive national income taxes combined with municipality-specific flat taxes.
- Mandatory employee social contributions (pension, unemployment, universal health insurance).
- Dynamic mortgage benchmarks (such as 12-month Euribor reference rates) and regulatory borrowing caps (e.g., Fin-FSA stress-testing rules).

Most online calculators are either locked to a single country, cluttered with ads, inaccurate due to floating-point rounding errors, or present confusing numerical figures with zero explanation.

### The OmniFinance Solution
OmniFinance is an **open, modular, and developer-friendly platform** that delivers:
1. **100% Deterministic Mathematical Accuracy**: All monetary calculations use Python’s `decimal.Decimal` (never standard floats) for zero-rounding-error compliance.
2. **AI Fiscal Intelligence via LLM**: Uses **Groq (`openai/gpt-oss-120b`)** via **LangChain** and **Pydantic Structured Outputs** to translate complex tax numbers into plain-language explanations and personalized tax-saving tips.
3. **Modular Country Pack System**: Expand to any new country (e.g., Sweden, Germany, Estonia) simply by adding a YAML configuration folder without modifying any core application code.
4. **Modern Fintech Aesthetics**: High-end glassmorphic UI, responsive pure-Python SVG visualizers (no Node.js/npm dependencies), dark/light mode, and full GDPR compliance.

---

## 🤖 Where Do We Use the LLM in This Project?

We implement a **Hybrid AI + Deterministic Architecture**: mathematical calculations are strictly handled by pure Python algorithms for guaranteed precision, while the Large Language Model (**Groq LLaMA 3.1 8B Instant**) provides semantic intelligence, regulatory analysis, and dynamic user explanations.

```
User Salary Inputs  ──►  Deterministic Tax Engine (app/countries/fi/tax.py)
                                  │
                          Exact Math & Brackets (Decimal)
                                  │
                                  ▼
                     Groq LLM Engine (app/ai/tax_agent.py)
                     Model: openai/gpt-oss-120b via LangChain
                                  │
                ┌─────────────────┴─────────────────┐
                ▼                                   ▼
   Structured Tax Law Extraction        Interactive User Explanation
   (CountryTaxLawExtraction)            (TaxExplanationResponse)
   - State Brackets                     - Where every euro goes
   - Social Security Rates              - Key takeaways & bullet points
   - Statutory Deductions               - Actionable Tax Optimization Tips
                                        - Interactive Q&A Drawer
```

### 1. Real-Time Tax Explanation & Synthesis
- **File**: [`app/ai/tax_agent.py`](file:///e:/FInance_app/app/ai/tax_agent.py)
- **Prompting & Output Model**: [`app/ai/schemas.py`](file:///e:/FInance_app/app/ai/schemas.py) &rarr; `TaxExplanationResponse`
- **What it does**: When a user computes their take-home pay, the LLM evaluates their gross income, municipality, and deduction breakdown. Rather than just showing numbers, it synthesizes an engaging headline, a detailed breakdown explaining where each euro goes (infrastructure, pension accrual, healthcare), and key bullet points.

### 2. Actionable Tax-Saving Tips & Deductions
- **Output Model**: `TaxOptimizationTip`
- **What it does**: The LLM suggests specific, legitimate tax deductions applicable to the user's jurisdiction. For Finland (Vero 2026), it highlights:
  - **Commuting Expenses (*Matkakulut*)**: Deducting public transit or car costs exceeding the threshold.
  - **Home Office Allowance (*Työhuonevähennys*)**: Standardized deductions for remote workers plus ergonomics.
  - **Household Maintenance Credit (*Kotitalousvähennys*)**: Tax credits for renovations, cleaning, and heat pump installations.

### 3. Country Tax Law Extraction & Structuring
- **Output Model**: `CountryTaxLawExtraction`
- **What it does**: Leverages Groq with LangChain's `PydanticOutputParser` to parse and extract structured tax law rules, progressive brackets, social security percentages, and official source citations into validated JSON/Pydantic objects.

### 4. Interactive AI Follow-Up Drawer
- **Template**: [`app/templates/partials/ai_drawer.html`](file:///e:/FInance_app/app/templates/partials/ai_drawer.html)
- **What it does**: Users can ask natural language questions directly in the calculator (e.g., *"How does working remotely 3 days a week affect my deductions?"* or *"What is TyEL pension?"*), and the Groq agent answers in context.

### 5. Resilient Offline Fallback
- If `GROQ_API_KEY` is not yet configured or if an external network issue occurs, the system automatically falls back to pre-seeded 2026 Finnish Tax Administration domain intelligence. **The site never crashes or displays empty screens.**

---

## ⚡ What Does the Platform Do? (Feature Breakdown)

### 1. Six Financial Calculators
Every calculator supports shareable GET query parameters, server-side validation, and instant visualization:

| Calculator | Key Inputs | Outputs & Capabilities |
| :--- | :--- | :--- |
| **Net Salary** | Gross salary, period (month/year), municipality, church member, age | Net income, progressive state tax, municipal tax, TyEL pension, unemployment insurance, SVG breakdown donut, and Groq AI tax advice. |
| **Loan Repayment** | Principal, interest rate, term (years), repayment type | Annuity vs. equal principal calculations, total interest, full amortization schedule, and dynamic SVG curve. |
| **Mortgage** | Property price, down payment, Euribor + bank margin, loan term | Loan-to-Value (LTV), monthly installment, and **+1% and +2% interest rate spike stress-testing**. |
| **Savings & Growth** | Initial deposit, monthly addition, annual rate, time horizon | Compound interest growth table, total deposits vs. interest earned, and **2% inflation-adjusted purchasing power**. |
| **Early Repayment** | Remaining balance, current payment, interest rate, extra prepayment | Exact interest saved, months and years shaved off the loan, and updated payoff date. |
| **Affordability** | Gross household income, existing monthly debt, available cash equity | Maximum borrowing capacity based on European Fin-FSA regulatory stress tests (40% DTI ceiling, 6% stress rate). |

### 2. Pure-Python SVG Chart Engine
- **File**: [`app/charts/svg_charts.py`](file:///e:/FInance_app/app/charts/svg_charts.py)
- Generates server-side, responsive SVG markup directly in Python.
- **Donut Visualizer**: Color-coded distribution of net pay, taxes, and social contributions.
- **Amortization Curve**: Dual-curve area graph visualizing principal reduction vs. cumulative bank interest.
- **No external JavaScript libraries, npm packages, or canvas renderers required.**

### 3. Country Pack Modularity
- Each country is completely self-contained in `app/countries/<iso2>/`:
  - `country.yaml`: Currencies, number formats, date formats, active calculators.
  - `tax_data_2026.yaml`: Brackets, municipal rates, social contribution percentages.
  - `tax.py`: Implementation of the `TaxEngine` interface.
  - `affiliates.yaml`: Localized financial partners (brokers, mortgages, personal loans).
  - `legal.yaml`: Disclaimers and privacy notices.
- **Scaffold a new country**:
  ```bash
  python scripts/new_country.py se Sweden SEK kr
  ```

### 4. Affiliate Monetization & Comparisons
- **Route**: `/{country}/{lang}/compare/{category}/`
- Structured comparison tables for stock brokers (e.g. Nordnet, DEGIRO), mortgage providers, and loan aggregators.
- Outbound click logging with anonymous telemetry via `/go/{partner_id}` and SQLite persistence.

### 5. SEO & Legal Compliance
- **SEO Ready**: Dynamic `sitemap.xml`, `robots.txt`, `ads.txt`, Schema.org `WebApplication` structured data, OpenGraph tags, and canonical URLs.
- **Programmatic SEO**: Pre-rendered landing pages for salary benchmarks (e.g., `/fi/en/salary/4000/`).
- **GDPR & Disclaimers**: Built-in cookie consent banner with localStorage preference storage, plus visible financial advice disclaimers.

---

## 📁 Repository Structure

```
E:\Finance_app\
├── app/
│   ├── main.py                     # FastAPI application factory & lifespan loader
│   ├── config.py                   # Pydantic BaseSettings & env handling
│   │
│   ├── ai/                         # Groq LLM & LangChain Tax Engine
│   │   ├── __init__.py
│   │   ├── schemas.py              # Pydantic structured output models
│   │   └── tax_agent.py            # ChatGroq integration & fallback engine
│   │
│   ├── calculators/                # 6 Pure-Python Calculators (Decimal precision)
│   │   ├── base.py                 # Abstract Calculator base class & Decimal utilities
│   │   ├── net_salary.py           # Take-home salary engine
│   │   ├── loan.py                 # Annuity & equal-principal loan calculator
│   │   ├── mortgage.py             # Mortgage & Euribor sensitivity stress-tester
│   │   ├── savings.py              # Compound interest & inflation deflator
│   │   ├── early_repayment.py      # Prepayment interest-saved calculator
│   │   └── affordability.py        # Fin-FSA regulatory borrowing limit engine
│   │
│   ├── charts/
│   │   └── svg_charts.py           # Pure-Python SVG donut & curve generators
│   │
│   ├── countries/                  # Country Pack Framework
│   │   ├── base.py                 # CountryPack & TaxEngine abstract models
│   │   ├── registry.py             # Auto-discovery & validation registry
│   │   ├── _template/              # Scaffold template for new nations
│   │   └── fi/                     # Finland 2026 Country Pack (Vero rules)
│   │       ├── country.yaml
│   │       ├── calculators.yaml
│   │       ├── affiliates.yaml
│   │       ├── legal.yaml
│   │       ├── tax_data_2026.yaml
│   │       └── tax.py
│   │
│   ├── db/                         # Database layer
│   │   ├── models.py               # SQLModel entities (Subscribers, Clicks, Events)
│   │   └── session.py              # SQLite session & engine factory
│   │
│   ├── services/                   # Business logic (i18n, ads, affiliates, seo)
│   ├── static/                     # CSS design system & client-side theme switcher
│   ├── templates/                  # Jinja2 HTML layouts, components, & partials
│   └── web/                        # FastAPI route controllers
│
├── scripts/
│   ├── new_country.py              # CLI tool to scaffold new country packs
│   └── validate_country_pack.py    # CI validator for tax data and completeness
│
├── tests/                          # Pytest suite (calculators, Vero fixtures, AI schemas)
├── Dockerfile                      # Production container image
├── docker-compose.yml              # Local multi-service orchestrator
├── Procfile                        # Cloud PaaS execution command
├── pyproject.toml                  # Project metadata
└── requirements.txt                # Python dependencies
```

---

## 🛠️ Installation & Setup

### 1. Clone & Setup Environment
```bash
git clone https://github.com/your-username/finance-platform.git
cd finance-platform
```

Create a virtual environment:
```bash
python -m venv myenv
# Windows:
.\myenv\Scripts\activate
# macOS/Linux:
source myenv/bin/activate
```

Install requirements:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your Groq API key (free at [console.groq.com](https://console.groq.com/keys)):
```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
APP_ENV=development
DEBUG=True
PORT=8000
```
*(If left empty, the application runs automatically using built-in Finnish Vero 2026 domain intelligence).*

### 3. Run Locally
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at:
- **Global Portal**: `http://localhost:8000/`
- **Finland Hub**: `http://localhost:8000/fi/en/`
- **Net Salary & Groq AI Insights**: `http://localhost:8000/fi/en/net_salary/`
- **Mortgage Stress Test**: `http://localhost:8000/fi/en/mortgage/`
- **System Health**: `http://localhost:8000/healthz`

### 4. Run with Docker
```bash
docker compose up --build
```

---

## 🧪 Testing & Validation

Run unit tests and calculator property assertions:
```bash
pytest
```

Validate a country pack against platform integrity rules:
```bash
python scripts/validate_country_pack.py fi
```

---

## ☁️ Cloud Deployment Guide

### Deploying to Render
1. Push this repository to GitHub.
2. In [Render Dashboard](https://render.com), create a **New Web Service**.
3. Set the following:
   - **Runtime**: `Python 3` (or `Docker`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
   - **Health Check Path**: `/healthz`
4. Set Environment Variables:
   - `GROQ_API_KEY`: *(your key)*
   - `APP_ENV`: `production`
   - `DEBUG`: `False`
5. Click **Deploy**.

### Deploying to Railway
1. Go to [Railway.app](https://railway.app) &rarr; **New Project** &rarr; **Deploy from GitHub**.
2. Railway detects the `Dockerfile` and `Procfile`.
3. Add `GROQ_API_KEY` under the **Variables** tab.
4. Generate a public domain under **Settings**.

### Deploying to Fly.io
```bash
fly launch
fly secrets set GROQ_API_KEY=gsk_your_key_here
fly deploy
```

---

## 📄 License & Disclaimer

- **License**: MIT License.
- **Financial Disclaimer**: All calculations and AI outputs are mathematical approximations for educational and informational purposes only and do not constitute certified tax, legal, or financial advice. Always verify rates with official local tax authorities (e.g. Vero in Finland).

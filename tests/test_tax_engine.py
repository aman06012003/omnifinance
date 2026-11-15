"""Tests for Finland 2026 Tax Engine."""
from decimal import Decimal
from pathlib import Path
import pytest

from app.countries.fi.tax import FITaxEngine

@pytest.fixture
def fi_engine():
    pack_dir = Path(__file__).resolve().parent.parent / "app" / "countries" / "fi"
    return FITaxEngine(pack_dir)

def test_finland_tax_engine_salaries(fi_engine):
    salaries = [Decimal("2500"), Decimal("3800"), Decimal("5500"), Decimal("8500")]

    for monthly in salaries:
        gross_annual = monthly * Decimal("12")
        result = fi_engine.gross_to_net(
            gross_annual=gross_annual,
            municipality="Helsinki",
            is_church_member=False,
            age=30,
        )

        assert result.net_annual < gross_annual
        assert result.net_monthly < monthly
        assert result.total_deductions > 0
        assert result.pension_contribution > 0
        assert result.unemployment_insurance > 0
        assert result.effective_rate_percent > 0
        assert len(result.breakdown) >= 4

def test_church_tax_toggle(fi_engine):
    gross_annual = Decimal("48000")

    res_no_church = fi_engine.gross_to_net(gross_annual, municipality="Helsinki", is_church_member=False)
    res_with_church = fi_engine.gross_to_net(gross_annual, municipality="Helsinki", is_church_member=True)

    assert res_no_church.church_tax == Decimal("0.00")
    assert res_with_church.church_tax > Decimal("0.00")
    assert res_with_church.net_annual < res_no_church.net_annual

def test_municipalities_loaded(fi_engine):
    munis = fi_engine.get_municipalities()
    assert len(munis) >= 5
    muni_names = [m.name for m in munis]
    assert "Helsinki" in muni_names
    assert "Tampere" in muni_names

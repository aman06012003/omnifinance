"""Base classes and precision Decimal helpers for all calculators."""
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict
from pydantic import BaseModel, Field

def round_curr(val: Any) -> Decimal:
    """Format and round strictly to 2 decimal places using standard ROUND_HALF_UP."""
    if val is None:
        return Decimal("0.00")
    if isinstance(val, (int, str)):
        return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if isinstance(val, float):
        return Decimal(f"{val:.2f}").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal("0.00")

def to_decimal(val: Any) -> Decimal:
    """Safely convert any numeric value to Decimal."""
    if val is None:
        return Decimal("0.0")
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))

class BaseCalculatorInput(BaseModel):
    country: str = Field(default="fi")
    lang: str = Field(default="en")

class BaseCalculatorResult(BaseModel):
    calculator_id: str
    country: str
    currency_symbol: str = "€"
    assumptions: Dict[str, Any] = Field(default_factory=dict)
    disclaimer: str = "Calculated for informational purposes only. Not certified financial advice."
    svg_chart: str = ""

class Calculator(ABC):
    """Abstract Base Class for all financial calculators."""

    id: str = "base"
    name: str = "Base Calculator"
    description: str = ""

    @abstractmethod
    def calculate(self, inputs: Dict[str, Any], country_pack: Any) -> BaseCalculatorResult:
        """Run computation with country pack context and return validated result model."""
        pass

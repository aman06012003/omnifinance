"""Validate that a country pack complies with all platform requirements."""
import sys
import datetime
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
COUNTRIES_DIR = BASE_DIR / "app" / "countries"

def validate_pack(country_code: str) -> bool:
    pack_dir = COUNTRIES_DIR / country_code.lower()
    if not pack_dir.exists():
        print(f"❌ Fail: Directory {pack_dir} does not exist.")
        return False

    errors = []

    # 1. Check country.yaml
    country_yaml = pack_dir / "country.yaml"
    if not country_yaml.exists():
        errors.append("Missing country.yaml")
    else:
        try:
            with open(country_yaml, "r", encoding="utf-8") as f:
                cdata = yaml.safe_load(f)
            if not cdata.get("code"):
                errors.append("country.yaml missing 'code'")
            if not cdata.get("currency"):
                errors.append("country.yaml missing 'currency'")
            tax_year = cdata.get("tax_year", 0)
            current_year = datetime.datetime.now().year
            if tax_year < current_year:
                errors.append(f"Tax year {tax_year} is outdated! Must be >= {current_year}")
        except Exception as e:
            errors.append(f"Invalid country.yaml format: {e}")

    # 2. Check calculators.yaml
    calc_yaml = pack_dir / "calculators.yaml"
    if not calc_yaml.exists():
        errors.append("Missing calculators.yaml")

    # 3. Check tax.py
    tax_py = pack_dir / "tax.py"
    if not tax_py.exists():
        errors.append("Missing tax.py")

    # 4. Check for TODO markers
    for fpath in pack_dir.rglob("*.py"):
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        if "TODO: verify" in text:
            errors.append(f"Unverified data marker found in {fpath.name}")

    if errors:
        print(f"❌ Country pack '{country_code}' failed validation:")
        for err in errors:
            print(f"   - {err}")
        return False

    print(f"✅ Country pack '{country_code}' passed all verification checks!")
    return True

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "fi"
    success = validate_pack(code)
    sys.exit(0 if success else 1)

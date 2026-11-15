"""Scaffold a new Country Pack from the template."""
import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
COUNTRIES_DIR = BASE_DIR / "app" / "countries"
TEMPLATE_DIR = COUNTRIES_DIR / "_template"

def scaffold_country(country_code: str, country_name: str, currency: str = "EUR", symbol: str = "€") -> None:
    code = country_code.lower().strip()
    target_dir = COUNTRIES_DIR / code

    if target_dir.exists():
        print(f"Error: Country directory '{code}' already exists at {target_dir}")
        sys.exit(1)

    print(f"Scaffolding new country pack '{country_name}' [{code}] from template...")
    shutil.copytree(TEMPLATE_DIR, target_dir)

    # Customize country.yaml
    country_yaml = target_dir / "country.yaml"
    content = country_yaml.read_text(encoding="utf-8")
    content = content.replace("code: xx", f"code: {code}")
    content = content.replace("name: Template Country", f"name: {country_name}")
    content = content.replace("domain_path: /xx", f"domain_path: /{code}")
    content = content.replace("currency: EUR", f"currency: {currency}")
    content = content.replace('currency_symbol: "€"', f'currency_symbol: "{symbol}"')
    country_yaml.write_text(content, encoding="utf-8")

    print(f"Country pack created at: {target_dir}")
    print(f"Next steps:")
    print(f"  1. Update {target_dir}/country.yaml")
    print(f"  2. Define tax rates in {target_dir}/tax.py")
    print(f"  3. Run: python scripts/validate_country_pack.py {code}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/new_country.py <iso2_code> <Country Name> [currency] [symbol]")
        print("Example: python scripts/new_country.py se Sweden SEK kr")
        sys.exit(1)

    c_code = sys.argv[1]
    c_name = sys.argv[2]
    c_curr = sys.argv[3] if len(sys.argv) > 3 else "EUR"
    c_sym = sys.argv[4] if len(sys.argv) > 4 else "€"

    scaffold_country(c_code, c_name, c_curr, c_sym)

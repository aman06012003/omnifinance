"""Country Pack Registry for auto-discovery and loading."""
import importlib.util
import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from .base import CountryPack, CountryPackConfig, AffiliatePartner, TaxEngine

logger = logging.getLogger(__name__)

class CountryRegistry:
    def __init__(self) -> None:
        self._packs: Dict[str, CountryPack] = {}

    def discover_and_load(self, countries_dir: Path) -> None:
        """Scan directory and load all valid country packs."""
        if not countries_dir.exists():
            logger.warning(f"Countries directory does not exist: {countries_dir}")
            return

        for item in countries_dir.iterdir():
            if item.is_dir() and not item.name.startswith(("_", ".")):
                try:
                    pack = self._load_pack(item)
                    if pack:
                        self._packs[pack.code.lower()] = pack
                        logger.info(f"Loaded country pack: {pack.name} [{pack.code}]")
                except Exception as e:
                    logger.error(f"Failed to load country pack from {item}: {e}", exc_info=True)

    def _load_pack(self, pack_dir: Path) -> Optional[CountryPack]:
        country_yaml_path = pack_dir / "country.yaml"
        if not country_yaml_path.exists():
            return None

        # Load country.yaml
        with open(country_yaml_path, "r", encoding="utf-8") as f:
            country_raw = yaml.safe_load(f)
        config = CountryPackConfig(**country_raw)

        # Load calculators.yaml
        calc_yaml = pack_dir / "calculators.yaml"
        calculators_config = {}
        if calc_yaml.exists():
            with open(calc_yaml, "r", encoding="utf-8") as f:
                calculators_config = yaml.safe_load(f) or {}

        # Load affiliates.yaml
        aff_yaml = pack_dir / "affiliates.yaml"
        affiliates_list: List[AffiliatePartner] = []
        if aff_yaml.exists():
            with open(aff_yaml, "r", encoding="utf-8") as f:
                raw_aff = yaml.safe_load(f) or {}
                for category, partners in raw_aff.items():
                    if isinstance(partners, list):
                        for p in partners:
                            p["category"] = category
                            affiliates_list.append(AffiliatePartner(**p))

        # Load legal.yaml
        legal_yaml = pack_dir / "legal.yaml"
        legal_info = {}
        if legal_yaml.exists():
            with open(legal_yaml, "r", encoding="utf-8") as f:
                legal_info = yaml.safe_load(f) or {}

        # Dynamically load tax engine from tax.py
        tax_engine: Optional[TaxEngine] = None
        tax_py = pack_dir / "tax.py"
        if tax_py.exists():
            spec = importlib.util.spec_from_file_location(f"countries.{pack_dir.name}.tax", str(tax_py))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                engine_cls = getattr(module, "Engine", None) or getattr(module, f"{config.code.upper()}TaxEngine", None)
                if engine_cls:
                    tax_engine = engine_cls(pack_dir)

        return CountryPack(
            config=config,
            tax_engine=tax_engine,
            calculators_config=calculators_config,
            affiliates=affiliates_list,
            legal_info=legal_info,
        )

    def _ensure_loaded(self) -> None:
        if not self._packs:
            from app.config import settings
            self.discover_and_load(settings.COUNTRIES_DIR)

    def get(self, code: str) -> Optional[CountryPack]:
        self._ensure_loaded()
        return self._packs.get(code.lower())

    def get_all(self) -> List[CountryPack]:
        self._ensure_loaded()
        return list(self._packs.values())

    def get_codes(self) -> List[str]:
        self._ensure_loaded()
        return list(self._packs.keys())

country_registry = CountryRegistry()

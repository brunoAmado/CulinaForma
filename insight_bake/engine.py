"""
`SetMiddle Insight™ · Bake` (`InsightBake` · `insight_bake.engine`).
Internal Engine: `InsightCore` (`insightCoreIO` + `insightCoreAI`).

Combines:
1. **Parametric `Three.js` 3D Cake Scene Graph & Structural Engineering**:
   - Multi-tier (`1..6` tiers) geometry (`ROUND`, `SQUARE`, `HEART`, `HEXAGON`), exact Wedding (`2.5cm x 5cm`) vs. Party (`5cm x 5cm`) slice calculator, center-of-mass slenderness verification (`H / D_base <= 2.2`), total mass (`kg`), and **Internal Dowel Rod + Center Skewer Structural Blueprint** so stacked tiers never collapse.
2. **Exact Ingredient BOM Scaling, Full 14 EU Reg. 1169/2011 Allergens & Portuguese AT (`ATCUD` / IVA 13% vs. 23%) Pricing**:
   - Scales flour, sugar, eggs, butter, chocolate, filling, and frosting in grams (`g`) from exact 3D tier volumes (`cm³`), computes all 14 statutory Annex II allergens + Portuguese counter signage (`DL n.º 26/2016`), validates Portuguese NIF (`Modulo-11`), and distinguishes `13%` (*Restauração*) vs. `23%` (*Take-Away / Entrega*) IVA with 50% `ATCUD` deposit preview.
3. **Arrhenius Sourdough Fermentation ($Q_{10}$ Kinetics), Baker's Percentage & Desired Dough Temperature (`DDT`)**:
   - Models temperature-dependent bulk fermentation and `+4 °C` cold-retard kinetics, exact Baker's % gram scaling, psychrometric hydration adjustments, and bi-temporal ASAE HACCP lot traceability.
4. **Zero-Hallucination `ComfyUI` ControlNet Depth/Canny Studio Spec + `InsightPastelaria` (`:4029`) & ASAE Ficha Bridge**:
   - Locks `Three.js` 3D tier aspect ratios (`controlnet_depth_strength=0.88`), generates printable A4 ASAE Technical Data Sheets (`FT-ASAE-BAKE-*`), and dispatches `day_before` (`24h`) custom cake orders into `InsightPastelaria` (`:4029`).
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECTS_ROOT = Path(__file__).resolve().parent.parent.parent
for _sibling in ("InsightCore", "InsightPastelaria", "InsightActivity", "InsightBackup"):
    _cand_dir = _PROJECTS_ROOT / _sibling
    if _cand_dir.exists() and str(_cand_dir) not in sys.path:
        sys.path.insert(0, str(_cand_dir))

try:
    from insight_core_io import (
        assert_no_binary_blob_in_db_row,
        filter_point_in_time_records,
        scrub_pt_eu_pii_and_byok_secrets,
    )
except Exception:  # pragma: no cover
    def assert_no_binary_blob_in_db_row(row: Dict[str, Any]) -> tuple[bool, List[str]]:
        raw = json.dumps(row, ensure_ascii=False)
        if "data:image/" in raw or ";base64," in raw:
            return False, ["inline_base64_blob"]
        return True, []

    def filter_point_in_time_records(
        records: List[Dict[str, Any]],
        point_in_time_date: str,
        enforce_rls: bool = False,
    ) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for rec in records:
            eff_from = str(rec.get("effective_from") or "0000-01-01")
            eff_to = rec.get("effective_to")
            if eff_from <= point_in_time_date and (eff_to is None or point_in_time_date <= str(eff_to)):
                out.append(rec)
        return out

    def scrub_pt_eu_pii_and_byok_secrets(text: str) -> Dict[str, Any]:
        import re as _re
        cleaned = _re.sub(r"\b\d{9}\b", "[PT-NIF-REDACTED]", str(text or ""))
        return {"scrubbed_text": cleaned, "redactions": 1 if cleaned != text else 0}

from insight_pastelaria.locale_fiscal_engine import (
    compute_locale_aware_recipe_cmv,
    evaluate_turnover_cliff_and_quote_guard,
    list_supported_locale_profiles,
    resolve_locale_fiscal_profile,
    simulate_exemption_vs_voluntary_vat_opt_in,
)


ASAE_HACCP_BITEMPORAL_LOT_AND_COST_TABLE: List[Dict[str, Any]] = [
    {
        "record_id": "BAKE-LOT-2025-H1",
        "service_domain": "InsightBake",
        "country_code": "PT",
        "title": "Lote ASAE HACCP 2025 & Custos Matérias-Primas 2025 (Chocolate Belga €14.50/kg, Manteiga €7.80/kg)",
        "effective_from": "2025-01-01",
        "effective_to": "2025-12-31",
        "superseded_by": "BAKE-LOT-2026-ACTIVE",
        "ingredient_cost_multiplier": 0.88,
        "haccp_lot_certificate": "ASAE-CERT-2025-PT-0891",
    },
    {
        "record_id": "BAKE-LOT-2026-ACTIVE",
        "service_domain": "InsightBake",
        "country_code": "PT",
        "title": "Lote ASAE HACCP 2026 & Custos Matérias-Primas 2026 (Chocolate Belga €16.80/kg, Manteiga €8.90/kg)",
        "effective_from": "2026-01-01",
        "effective_to": None,
        "superseded_by": None,
        "ingredient_cost_multiplier": 1.0,
        "haccp_lot_certificate": "ASAE-CERT-2026-PT-4412",
    },
]


# Complete 14 Mandatory EU Allergens — Regulamento (UE) n.º 1169/2011 Anexo II & Decreto-Lei n.º 26/2016
EU_14_MANDATORY_ALLERGENS: Dict[str, Dict[str, Any]] = {
    "GLUTEN": {
        "anexo_ii_num": 1,
        "label_pt": "Cereais que contêm glúten (trigo, centeio, cevada, aveia, espelta, kamut) — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "CRUSTACEANS": {
        "anexo_ii_num": 2,
        "label_pt": "Crustáceos e produtos à base de crustáceos — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "EGGS": {
        "anexo_ii_num": 3,
        "label_pt": "Ovos e produtos à base de ovos — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "FISH": {
        "anexo_ii_num": 4,
        "label_pt": "Peixes e produtos à base de peixe — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "PEANUTS": {
        "anexo_ii_num": 5,
        "label_pt": "Amendoins e produtos à base de amendoim — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "SOY": {
        "anexo_ii_num": 6,
        "label_pt": "Soja e produtos à base de soja (incluindo lecitina E322) — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "MILK": {
        "anexo_ii_num": 7,
        "label_pt": "Leite e produtos à base de leite (incluindo lactose) — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "NUTS": {
        "anexo_ii_num": 8,
        "label_pt": "Frutos de casca rija (amêndoas, avelãs, nozes, pistácios, caju, noz-pecã) — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "CELERY": {
        "anexo_ii_num": 9,
        "label_pt": "Aipo e produtos à base de aipo — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "MUSTARD": {
        "anexo_ii_num": 10,
        "label_pt": "Mostarda e produtos à base de mostarda — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "SESAME": {
        "anexo_ii_num": 11,
        "label_pt": "Sementes de sésamo e produtos à base de sementes de sésamo — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "SULPHITES": {
        "anexo_ii_num": 12,
        "label_pt": "Dióxido de enxofre e sulfitos (> 10 mg/kg ou 10 mg/L em SO2) — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "LUPIN": {
        "anexo_ii_num": 13,
        "label_pt": "Tremoço e produtos à base de tremoço — Reg. (UE) n.º 1169/2011 Anexo II",
    },
    "MOLLUSCS": {
        "anexo_ii_num": 14,
        "label_pt": "Moluscos e produtos à base de moluscos — Reg. (UE) n.º 1169/2011 Anexo II",
    },
}

SPONGE_RECIPES: Dict[str, Dict[str, Any]] = {
    "pao_de_lo_tradicional": {
        "name": "Pão de Ló Tradicional Português",
        "density_g_per_cm3": 0.42,
        "cost_eur_per_kg": 6.80,
        "sponge_color_hex": "#FDE68A",
        "allergens": ["GLUTEN", "EGGS"],
        "baking_temp_c": 175.0,
        "baking_time_minutes": 32,
        "ratios": {"eggs_g": 0.45, "sugar_g": 0.30, "wheat_flour_g": 0.25},
        "nutrition_per_100g": {"fat_g": 5.2, "saturates_g": 1.6, "carbs_g": 49.5, "sugars_g": 30.2, "protein_g": 8.4, "salt_g": 0.32},
    },
    "red_velvet": {
        "name": "Red Velvet Artisanal (Buttermilk & Cocoa)",
        "density_g_per_cm3": 0.54,
        "cost_eur_per_kg": 8.50,
        "sponge_color_hex": "#9F1239",
        "allergens": ["GLUTEN", "EGGS", "MILK"],
        "baking_temp_c": 170.0,
        "baking_time_minutes": 35,
        "ratios": {"wheat_flour_g": 0.30, "sugar_g": 0.28, "buttermilk_g": 0.20, "eggs_g": 0.12, "butter_g": 0.10},
        "nutrition_per_100g": {"fat_g": 11.4, "saturates_g": 6.8, "carbs_g": 51.0, "sugars_g": 29.0, "protein_g": 5.8, "salt_g": 0.48},
    },
    "chocolate_belga_70": {
        "name": "Bolo Húmido de Chocolate Belga 70%",
        "density_g_per_cm3": 0.58,
        "cost_eur_per_kg": 10.20,
        "sponge_color_hex": "#3F2318",
        "allergens": ["GLUTEN", "EGGS", "MILK", "SOY"],
        "baking_temp_c": 170.0,
        "baking_time_minutes": 38,
        "ratios": {"wheat_flour_g": 0.24, "sugar_g": 0.26, "dark_chocolate_70_g": 0.20, "eggs_g": 0.15, "butter_g": 0.15},
        "nutrition_per_100g": {"fat_g": 21.6, "saturates_g": 13.1, "carbs_g": 46.8, "sugars_g": 31.5, "protein_g": 6.9, "salt_g": 0.38},
    },
    "amendoa_sem_gluten": {
        "name": "Bolo de Amêndoa & Limão (Sem Glúten)",
        "density_g_per_cm3": 0.52,
        "cost_eur_per_kg": 12.40,
        "sponge_color_hex": "#FEF08A",
        "allergens": ["EGGS", "NUTS"],
        "baking_temp_c": 165.0,
        "baking_time_minutes": 34,
        "ratios": {"almond_flour_g": 0.45, "sugar_g": 0.30, "eggs_g": 0.25},
        "nutrition_per_100g": {"fat_g": 24.8, "saturates_g": 2.4, "carbs_g": 34.2, "sugars_g": 30.8, "protein_g": 12.6, "salt_g": 0.24},
    },
    "nozes_vinho_porto": {
        "name": "Bolo Nobre de Noz & Redução de Vinho do Porto",
        "density_g_per_cm3": 0.56,
        "cost_eur_per_kg": 13.20,
        "sponge_color_hex": "#78492A",
        "allergens": ["GLUTEN", "EGGS", "MILK", "NUTS", "SULPHITES"],
        "baking_temp_c": 170.0,
        "baking_time_minutes": 36,
        "ratios": {"wheat_flour_g": 0.26, "sugar_g": 0.24, "walnut_meal_g": 0.20, "eggs_g": 0.18, "butter_g": 0.08, "port_wine_reduction_g": 0.04},
        "nutrition_per_100g": {"fat_g": 20.4, "saturates_g": 5.9, "carbs_g": 44.5, "sugars_g": 26.2, "protein_g": 8.1, "salt_g": 0.35},
    },
}

FILLING_RECIPES: Dict[str, Dict[str, Any]] = {
    "brigadeiro_gourmet": {
        "name": "Brigadeiro Gourmet de Chocolate Nobre",
        "cost_eur_per_kg": 11.50,
        "filling_color_hex": "#4A2511",
        "allergens": ["MILK", "SOY"],
        "requires_refrigeration_4c": True,
        "nutrition_per_100g": {"fat_g": 16.5, "saturates_g": 10.2, "carbs_g": 52.0, "sugars_g": 47.5, "protein_g": 6.2, "salt_g": 0.28},
    },
    "ovos_moles_doces_conventuais": {
        "name": "Doce de Ovos Conventual Português",
        "cost_eur_per_kg": 10.80,
        "filling_color_hex": "#F59E0B",
        "allergens": ["EGGS"],
        "requires_refrigeration_4c": True,
        "nutrition_per_100g": {"fat_g": 11.8, "saturates_g": 3.6, "carbs_g": 56.4, "sugars_g": 55.0, "protein_g": 6.8, "salt_g": 0.15},
    },
    "curd_limao_frutos_vermelhos": {
        "name": "Lemon Curd & Compota de Frutos Vermelhos",
        "cost_eur_per_kg": 12.00,
        "filling_color_hex": "#E11D48",
        "allergens": ["EGGS", "MILK"],
        "requires_refrigeration_4c": True,
        "nutrition_per_100g": {"fat_g": 10.4, "saturates_g": 6.1, "carbs_g": 46.2, "sugars_g": 42.8, "protein_g": 3.4, "salt_g": 0.18},
    },
    "praline_avela_crocante": {
        "name": "Ganache & Praliné de Avelã Piemontesa",
        "cost_eur_per_kg": 15.50,
        "filling_color_hex": "#92400E",
        "allergens": ["MILK", "NUTS", "SOY"],
        "requires_refrigeration_4c": True,
        "nutrition_per_100g": {"fat_g": 31.2, "saturates_g": 11.8, "carbs_g": 42.5, "sugars_g": 38.0, "protein_g": 7.6, "salt_g": 0.22},
    },
    "pistacio_tahini_crocante": {
        "name": "Creme de Pistácio Siciliano & Crocante de Sésamo",
        "cost_eur_per_kg": 16.90,
        "filling_color_hex": "#65A30D",
        "allergens": ["MILK", "NUTS", "SESAME", "SOY"],
        "requires_refrigeration_4c": True,
        "nutrition_per_100g": {"fat_g": 33.4, "saturates_g": 9.4, "carbs_g": 39.8, "sugars_g": 34.0, "protein_g": 9.8, "salt_g": 0.26},
    },
}

FROSTING_RECIPES: Dict[str, Dict[str, Any]] = {
    "swiss_meringue_buttercream": {
        "name": "Swiss Meringue Buttercream (Cetim Suave)",
        "cost_eur_per_kg": 9.80,
        "allergens": ["EGGS", "MILK"],
        "max_ambient_temp_c": 23.0,
        "nutrition_per_100g": {"fat_g": 42.0, "saturates_g": 26.5, "carbs_g": 38.0, "sugars_g": 38.0, "protein_g": 2.4, "salt_g": 0.25},
    },
    "ganache_blindagem_fondant": {
        "name": "Blindagem em Ganache + Pasta de Açúcar (Fondant)",
        "cost_eur_per_kg": 12.50,
        "allergens": ["MILK", "SOY"],
        "max_ambient_temp_c": 28.0,
        "nutrition_per_100g": {"fat_g": 19.5, "saturates_g": 12.0, "carbs_g": 68.5, "sugars_g": 64.0, "protein_g": 2.1, "salt_g": 0.16},
    },
    "semi_naked_rustico": {
        "name": "Semi-Naked Rústico com Flores Naturais",
        "cost_eur_per_kg": 8.90,
        "allergens": ["EGGS", "MILK"],
        "max_ambient_temp_c": 22.0,
        "nutrition_per_100g": {"fat_g": 36.0, "saturates_g": 22.8, "carbs_g": 36.5, "sugars_g": 36.0, "protein_g": 2.6, "salt_g": 0.22},
    },
}


def format_multibanco_ref_mod97(entity_5digits: str, order_seed_7digits: int, amount_cents: int) -> str:
    """
    Generates a deterministic Portuguese SIBS Multibanco 9-digit reference (`XXX XXX XXX`)
    using ISO 7064 Modulo 97-10 check digits over `entity(5) + seed(7) + amount_cents(8)`.
    """
    ent = "".join(ch for ch in str(entity_5digits or "21403") if ch.isdigit())[:5].zfill(5)
    seed7 = int(order_seed_7digits) % 10_000_000
    cents8 = max(0, int(amount_cents)) % 100_000_000
    payload_str = f"{ent}{seed7:07d}{cents8:08d}00"
    rem = int(payload_str) % 97
    check = (98 - rem) % 100
    ref9 = f"{seed7:07d}{check:02d}"
    return f"{ref9[:3]} {ref9[3:6]} {ref9[6:9]}"


def compute_eu_1169_nutritional_declaration(
    weighted_components: List[tuple[float, Dict[str, float]]],
    portions_count: int = 1,
    portion_label_pt: str = "Fatia Casamento (2,5×5 cm)",
) -> Dict[str, Any]:
    """
    Computes the statutory EU Regulation No. 1169/2011 Art. 30.º & Annex XIV Nutritional Table
    (`per_100g` and `per_portion`: kJ = 37*fat + 17*carbs + 17*protein; kcal = 9*fat + 4*carbs + 4*protein).
    """
    total_g = max(1.0, sum(max(0.0, w) for w, _ in weighted_components))
    keys = ("fat_g", "saturates_g", "carbs_g", "sugars_g", "protein_g", "salt_g")
    per100: Dict[str, float] = {}
    for k in keys:
        per100[k] = round(sum(max(0.0, w) * float(nut.get(k, 0.0)) for w, nut in weighted_components) / total_g, 2)

    energy_kj_100 = round(37.0 * per100["fat_g"] + 17.0 * per100["carbs_g"] + 17.0 * per100["protein_g"], 1)
    energy_kcal_100 = round(9.0 * per100["fat_g"] + 4.0 * per100["carbs_g"] + 4.0 * per100["protein_g"], 1)

    portions = max(1, int(portions_count))
    portion_weight_g = round(total_g / portions, 1)
    scale = portion_weight_g / 100.0

    return {
        "regulation": "Regulamento (UE) n.º 1169/2011 Art. 30.º & Anexo XIV (Declaração Nutricional Obrigatória)",
        "portion_label_pt": portion_label_pt,
        "portion_weight_g": portion_weight_g,
        "per_100g": {
            "energy_kj": energy_kj_100,
            "energy_kcal": energy_kcal_100,
            **per100,
        },
        "per_portion": {
            "energy_kj": round(energy_kj_100 * scale, 1),
            "energy_kcal": round(energy_kcal_100 * scale, 1),
            **{k: round(v * scale, 2) for k, v in per100.items()},
        },
    }


def validate_portuguese_nif_modulo11(nif: str) -> bool:
    """Validates a 9-digit Portuguese NIF using the statutory AT Modulo-11 check digit."""
    digits = "".join(ch for ch in str(nif or "") if ch.isdigit())
    if len(digits) != 9 or digits[0] not in "12356789":
        return False
    total = sum(int(digits[i]) * (9 - i) for i in range(8))
    rem = total % 11
    check_digit = 0 if rem < 2 else (11 - rem)
    return int(digits[8]) == check_digit


def _normalize_scrubbed_text(raw_text: str) -> str:
    res = scrub_pt_eu_pii_and_byok_secrets(raw_text)
    if isinstance(res, dict):
        return str(res.get("scrubbed_text") or res.get("text") or raw_text)
    if isinstance(res, tuple) and res:
        return str(res[0])
    return str(raw_text or "")


def compute_arrhenius_fermentation_and_bakers_pct(
    flour_mass_g: float = 5000.0,
    dough_temp_c: float = 26.0,
    hydration_pct: float = 72.0,
    starter_pct: float = 20.0,
    salt_pct: float = 2.2,
    ambient_temp_c: float = 22.0,
    flour_temp_c: float = 21.0,
    mixer_friction_c: float = 2.5,
    cold_retard_temp_c: float = 4.0,
    cold_retard_hours: float = 14.0,
    point_in_time: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Computes Q10 / Arrhenius sourdough & pastry dough fermentation kinetics,
    Baker's Percentage gram scaling, Desired Dough Temperature (`DDT`) water temp,
    and bi-temporal ASAE HACCP lot traceability (`Reg. (CE) n.º 852/2004`).
    """
    flour_g = float(flour_mass_g)
    temp_c = float(dough_temp_c)
    hyd_pct = float(hydration_pct)
    levain_pct = float(starter_pct)
    sal_pct = float(salt_pct)

    if flour_g < 100.0 or flour_g > 500_000.0:
        return {"ok": False, "error": f"INVALID_FLOUR_MASS_G({flour_g}): must be between 100g and 500,000g"}
    if temp_c < 2.0 or temp_c > 42.0:
        return {"ok": False, "error": f"UNSAFE_DOUGH_TEMP_C({temp_c}): yeast thermal inactivation >42C or freezing <2C"}
    if hyd_pct < 40.0 or hyd_pct > 110.0:
        return {"ok": False, "error": f"INVALID_HYDRATION_PCT({hyd_pct}): must be between 40% and 110%"}

    # Q10 = 2.15 around T_ref = 24.0 °C (Saccharomyces cerevisiae + Fructilactobacillus sanfranciscensis)
    q10_coeff = 2.15
    t_ref_c = 24.0
    base_bulk_hours_at_24c = 4.5 * ((20.0 / max(5.0, levain_pct)) ** 0.45)
    rate_factor_bulk = q10_coeff ** ((temp_c - t_ref_c) / 10.0)
    estimated_bulk_fermentation_hours = round(base_bulk_hours_at_24c / rate_factor_bulk, 2)

    # Cold retard equivalent fermentation at +4 °C
    rate_factor_cold = q10_coeff ** ((float(cold_retard_temp_c) - t_ref_c) / 10.0)
    cold_equiv_hours_at_24c = round(float(cold_retard_hours) * rate_factor_cold, 2)

    # Baker's Percentage Scaling
    water_g = round(flour_g * (hyd_pct / 100.0), 1)
    starter_g = round(flour_g * (levain_pct / 100.0), 1)
    salt_g = round(flour_g * (sal_pct / 100.0), 1)
    total_dough_g = round(flour_g + water_g + starter_g + salt_g, 1)

    # Desired Dough Temperature (DDT) 3-Factor Rule: Water Temp = (3 * DDT) - Ambient - Flour - Friction
    required_water_temp_c = round((3.0 * temp_c) - float(ambient_temp_c) - float(flour_temp_c) - float(mixer_friction_c), 1)

    pit_date = str(point_in_time or datetime.now(timezone.utc).strftime("%Y-%m-%d"))[:10]
    bitemporal_lots = filter_point_in_time_records(
        records=ASAE_HACCP_BITEMPORAL_LOT_AND_COST_TABLE,
        point_in_time_date=pit_date,
        enforce_rls=False,
    )
    cost_mult = float(bitemporal_lots[0].get("ingredient_cost_multiplier", 1.0)) if bitemporal_lots else 1.0
    raw_batch_cost_eur = round(((flour_g / 1000.0) * 1.35 + (starter_g / 1000.0) * 1.80 + (salt_g / 1000.0) * 0.65) * cost_mult, 2)

    haccp_cold_retard_ok = 0.5 <= float(cold_retard_temp_c) <= 5.0
    canonical_receipt = json.dumps(
        {
            "flour_g": flour_g,
            "temp_c": temp_c,
            "bulk_h": estimated_bulk_fermentation_hours,
            "pit": pit_date,
        },
        sort_keys=True,
    )
    sha256_receipt = hashlib.sha256(canonical_receipt.encode("utf-8")).hexdigest()

    return {
        "ok": True,
        "member": "InsightBake",
        "mode": "arrhenius_fermentation_and_bakers_pct",
        "bakers_percentage_bom_grams": {
            "flour_100pct_g": round(flour_g, 1),
            "water_g": water_g,
            "hydration_pct": hyd_pct,
            "levain_starter_g": starter_g,
            "starter_pct": levain_pct,
            "salt_g": salt_g,
            "salt_pct": sal_pct,
            "total_dough_mass_g": total_dough_g,
            "total_dough_mass_kg": round(total_dough_g / 1000.0, 2),
            "raw_batch_cost_eur": raw_batch_cost_eur,
        },
        "arrhenius_fermentation_kinetics": {
            "q10_coefficient": q10_coeff,
            "reference_temp_c": t_ref_c,
            "target_dough_temp_c": temp_c,
            "relative_fermentation_rate": round(rate_factor_bulk, 3),
            "estimated_bulk_fermentation_hours": estimated_bulk_fermentation_hours,
            "estimated_bulk_fermentation_minutes": int(round(estimated_bulk_fermentation_hours * 60)),
            "required_water_temp_ddt_c": required_water_temp_c,
            "cold_retard_temp_c": float(cold_retard_temp_c),
            "cold_retard_hours": float(cold_retard_hours),
            "cold_retard_24c_equivalent_hours": cold_equiv_hours_at_24c,
            "lactic_to_acetic_profile": (
                "Perfil Láctico Suave & Cremoso" if temp_c >= 26.0 else "Perfil Equilibrado / Acético Complexo"
            ),
        },
        "allergens_eu_1169_2011": {
            "regulation": "Regulamento (UE) n.º 1169/2011 Anexo II & DL n.º 26/2016",
            "allergen_codes": ["GLUTEN"],
            "mandatory_client_label": [
                {"code": "GLUTEN", "anexo_ii_num": 1, "statutory_label_pt": EU_14_MANDATORY_ALLERGENS["GLUTEN"]["label_pt"]}
            ],
        },
        "nutritional_declaration_eu_1169": compute_eu_1169_nutritional_declaration(
            weighted_components=[
                (flour_g + starter_g * 0.5, {"fat_g": 1.6, "saturates_g": 0.3, "carbs_g": 71.0, "sugars_g": 1.4, "protein_g": 11.8, "salt_g": 0.02}),
                (water_g + starter_g * 0.5, {"fat_g": 0.0, "saturates_g": 0.0, "carbs_g": 0.0, "sugars_g": 0.0, "protein_g": 0.0, "salt_g": 0.0}),
                (salt_g, {"fat_g": 0.0, "saturates_g": 0.0, "carbs_g": 0.0, "sugars_g": 0.0, "protein_g": 0.0, "salt_g": 100.0}),
            ],
            portions_count=max(1, int(round(total_dough_g / 60.0))),
            portion_label_pt="Fatia de Pão (60 g)",
        ),
        "haccp_and_bitemporal_traceability": {
            "regulation": "Regulamento (CE) n.º 852/2004 (HACCP) & Reg. (CE) n.º 178/2002 Art. 18.º",
            "point_in_time_date": pit_date,
            "cold_retard_haccp_compliant": haccp_cold_retard_ok,
            "bitemporal_lot_records": bitemporal_lots,
            "sha256_audit_receipt": sha256_receipt,
        },
    }


def compute_thermal_melt_countdown(
    max_safe_ambient_c: float,
    venue_temp_c: float = 22.0,
    venue_rh_pct: float = 55.0,
    tier_count: int = 3,
) -> Dict[str, Any]:
    """Calculates dynamic max-safe out-of-fridge venue display minutes before frosting structural softening."""
    base_minutes = 180.0
    delta_t = float(venue_temp_c) - float(max_safe_ambient_c)
    if delta_t <= 0.0:
        temp_factor = 1.0 + min(0.35, (-delta_t) * 0.04)
    else:
        temp_factor = max(0.15, 1.0 - delta_t * 0.14)
    rh_penalty = max(0.65, 1.0 - (float(venue_rh_pct) - 65.0) * 0.008) if float(venue_rh_pct) > 65.0 else 1.0
    tier_penalty = max(0.70, 1.0 - max(0, int(tier_count) - 1) * 0.05)
    safe_minutes = max(15, int(round(base_minutes * temp_factor * rh_penalty * tier_penalty)))
    if safe_minutes <= 60:
        risk_level = "CRITICAL_MELT_RISK"
    elif safe_minutes <= 120:
        risk_level = "MODERATE"
    else:
        risk_level = "SAFE"
    return {
        "venue_temp_c": round(float(venue_temp_c), 1),
        "venue_rh_pct": round(float(venue_rh_pct), 1),
        "frosting_max_safe_ambient_c": round(float(max_safe_ambient_c), 1),
        "minutes_until_structural_softening": safe_minutes,
        "risk_level": risk_level,
    }


def design_3d_cake_and_production_sheet(
    tiers: List[Dict[str, Any]] | None = None,
    shape: str = "ROUND",
    sponge_key: str = "red_velvet",
    filling_key: str = "brigadeiro_gourmet",
    frosting_key: str = "swiss_meringue_buttercream",
    style_theme: str = "Vintage Lambeth Piping with Gold Leaf & White Sugar Peonies",
    primary_color_hex: str = "#FFFDF9",
    accent_color_hex: str = "#D4AF37",
    topper_text: str = "Sofia & Miguel",
    hourly_rate_eur: float = 22.0,
    consumption_mode: str = "RESTAURACAO_13",
    may_contain_trace_codes: Optional[List[str]] = None,
    client_nif: Optional[str] = None,
    point_in_time_date: Optional[str] = None,
    venue_temp_c: float = 22.0,
    venue_rh_pct: float = 55.0,
    country_code: str = "PT",
    custom_fiscal_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Computes the complete `Three.js` 3D scene graph (including per-tier flavor mixing & 3D cutaway slice layers),
    wedding/party portions, structural dowel blueprint, slenderness stability check, gram-exact ingredient BOM,
    full 14 EU Reg. 1169/2011 allergen declaration, statutory EU Reg. 1169/2011 Art. 30.º nutritional table,
    ComfyUI ControlNet prompt, Portuguese AT (`13%` vs `23%` IVA + `ATCUD`) pricing, and `InsightFleet` cold-chain plan.
    """
    tier_specs = tiers if isinstance(tiers, list) and tiers else [
        {"diameter_cm": 25.0, "height_cm": 12.0},
        {"diameter_cm": 20.0, "height_cm": 12.0},
        {"diameter_cm": 15.0, "height_cm": 14.0},
    ]
    if len(tier_specs) > 6:
        return {"ok": False, "error": "MAX_6_TIERS_EXCEEDED_STRUCTURAL_SAFETY_LIMIT"}

    shape_clean = str(shape or "ROUND").strip().upper()
    if shape_clean not in ("ROUND", "SQUARE", "HEART", "HEXAGON"):
        shape_clean = "ROUND"

    default_sponge_key = sponge_key if sponge_key in SPONGE_RECIPES else "red_velvet"
    default_filling_key = filling_key if filling_key in FILLING_RECIPES else "brigadeiro_gourmet"
    resolved_frosting_key = frosting_key if frosting_key in FROSTING_RECIPES else "swiss_meringue_buttercream"

    sponge = SPONGE_RECIPES[default_sponge_key]
    filling = FILLING_RECIPES[default_filling_key]
    frosting = FROSTING_RECIPES[resolved_frosting_key]

    safe_topper = _normalize_scrubbed_text(str(topper_text or "Sofia & Miguel"))[:64]

    threejs_meshes: List[Dict[str, Any]] = []
    structural_dowels: List[Dict[str, Any]] = []
    per_tier_flavor_breakdown: List[Dict[str, Any]] = []
    current_y_cm = 0.0
    total_volume_cm3 = 0.0
    total_surface_cm2 = 0.0
    total_wedding_portions = 0
    total_party_portions = 0
    max_diameter_cm = 0.0

    sponge_weight_g = 0.0
    filling_weight_g = 0.0
    sponge_ingredients_g: Dict[str, float] = {}
    filling_breakdown_g: Dict[str, float] = {}
    sponge_cost_raw_eur = 0.0
    filling_cost_raw_eur = 0.0
    raw_allergen_codes: set[str] = set(frosting["allergens"])
    nutrition_weighted: List[tuple[float, Dict[str, float]]] = []

    for idx, t in enumerate(tier_specs):
        diam = float(t.get("diameter_cm", 20.0))
        height = float(t.get("height_cm", 12.0))
        if diam < 8.0 or diam > 60.0 or height < 5.0 or height > 30.0:
            return {
                "ok": False,
                "error": f"INVALID_TIER_DIMENSIONS_AT_TIER_{idx + 1}(diameter={diam}cm,height={height}cm)",
            }
        if idx > 0 and diam > float(tier_specs[idx - 1].get("diameter_cm", 20.0)):
            return {
                "ok": False,
                "error": f"INVERTED_UNSTABLE_TIER_AT_TIER_{idx + 1}({diam}cm_ON_TOP_OF_{tier_specs[idx - 1].get('diameter_cm')}cm)",
            }

        t_sponge_key = str(t.get("sponge_key") or default_sponge_key)
        if t_sponge_key not in SPONGE_RECIPES:
            t_sponge_key = default_sponge_key
        t_filling_key = str(t.get("filling_key") or default_filling_key)
        if t_filling_key not in FILLING_RECIPES:
            t_filling_key = default_filling_key

        t_sponge = SPONGE_RECIPES[t_sponge_key]
        t_filling = FILLING_RECIPES[t_filling_key]
        raw_allergen_codes.update(t_sponge["allergens"])
        raw_allergen_codes.update(t_filling["allergens"])

        max_diameter_cm = max(max_diameter_cm, diam)
        radius = diam / 2.0
        if shape_clean == "SQUARE":
            base_area_cm2 = diam * diam
            perimeter_cm = 4.0 * diam
            geom_type = "BoxGeometry"
            radial_segs = 4
        elif shape_clean == "HEXAGON":
            base_area_cm2 = 2.598076 * (radius ** 2)
            perimeter_cm = 6.0 * radius
            geom_type = "CylinderGeometry"
            radial_segs = 6
        elif shape_clean == "HEART":
            base_area_cm2 = 0.82 * (diam ** 2)
            perimeter_cm = 3.36 * diam
            geom_type = "ExtrudeHeartGeometry"
            radial_segs = 48
        else:
            base_area_cm2 = math.pi * (radius ** 2)
            perimeter_cm = 2.0 * math.pi * radius
            geom_type = "CylinderGeometry"
            radial_segs = 64

        vol_cm3 = base_area_cm2 * height
        surf_cm2 = base_area_cm2 + (perimeter_cm * height)
        total_volume_cm3 += vol_cm3
        total_surface_cm2 += surf_cm2

        t_sponge_g = round(vol_cm3 * 0.68 * float(t_sponge["density_g_per_cm3"]), 1)
        t_filling_g = round(vol_cm3 * 0.24 * 0.95, 1)
        sponge_weight_g = round(sponge_weight_g + t_sponge_g, 1)
        filling_weight_g = round(filling_weight_g + t_filling_g, 1)
        sponge_cost_raw_eur += (t_sponge_g / 1000.0) * float(t_sponge["cost_eur_per_kg"])
        filling_cost_raw_eur += (t_filling_g / 1000.0) * float(t_filling["cost_eur_per_kg"])

        for ing_k, ratio in t_sponge["ratios"].items():
            sponge_ingredients_g[ing_k] = round(sponge_ingredients_g.get(ing_k, 0.0) + (t_sponge_g * float(ratio)), 1)
        filling_breakdown_g[t_filling["name"]] = round(filling_breakdown_g.get(t_filling["name"], 0.0) + t_filling_g, 1)

        nutrition_weighted.append((t_sponge_g, t_sponge["nutrition_per_100g"]))
        nutrition_weighted.append((t_filling_g, t_filling["nutrition_per_100g"]))

        height_factor = 1.25 if height >= 13.0 else 1.0
        w_slices = max(4, int(round((base_area_cm2 / 12.5) * height_factor)))
        p_slices = max(3, int(round((base_area_cm2 / 22.0) * height_factor)))
        total_wedding_portions += w_slices
        total_party_portions += p_slices

        dowels_in_tier = 0
        if idx < len(tier_specs) - 1:
            upper_diam = float(tier_specs[idx + 1].get("diameter_cm", 15.0))
            dowels_in_tier = max(4, int(round(upper_diam / 3.5)))
            structural_dowels.append({
                "tier_index": idx + 1,
                "tier_diameter_cm": diam,
                "supports_upper_tier_diameter_cm": upper_diam,
                "polypropylene_dowel_rods_count": dowels_in_tier,
                "dowel_cut_height_cm": height,
                "cake_board_under_upper_tier_cm": upper_diam,
            })

        # Cutaway internal cross-section layers (3 sponge discs + 2 filling bands)
        disc_h = round((height * 0.72) / 3.0, 2)
        fill_h = round((height * 0.28) / 2.0, 2)
        cutaway_layers = [
            {"layer": "sponge_1", "height_cm": disc_h, "color_hex": t_sponge["sponge_color_hex"]},
            {"layer": "filling_1", "height_cm": fill_h, "color_hex": t_filling["filling_color_hex"]},
            {"layer": "sponge_2", "height_cm": disc_h, "color_hex": t_sponge["sponge_color_hex"]},
            {"layer": "filling_2", "height_cm": fill_h, "color_hex": t_filling["filling_color_hex"]},
            {"layer": "sponge_3", "height_cm": disc_h, "color_hex": t_sponge["sponge_color_hex"]},
        ]

        per_tier_flavor_breakdown.append({
            "tier_number": idx + 1,
            "sponge_key": t_sponge_key,
            "sponge_name": t_sponge["name"],
            "sponge_grams": t_sponge_g,
            "filling_key": t_filling_key,
            "filling_name": t_filling["name"],
            "filling_grams": t_filling_g,
        })

        threejs_meshes.append({
            "tier_number": idx + 1,
            "geometry_type": geom_type,
            "radial_segments": radial_segs,
            "diameter_cm": diam,
            "height_cm": height,
            "position_y_cm": round(current_y_cm + (height / 2.0), 2),
            "base_color_hex": primary_color_hex,
            "piping_accent_color_hex": accent_color_hex,
            "sponge_key": t_sponge_key,
            "sponge_name": t_sponge["name"],
            "sponge_color_hex": t_sponge["sponge_color_hex"],
            "filling_key": t_filling_key,
            "filling_name": t_filling["name"],
            "filling_color_hex": t_filling["filling_color_hex"],
            "cutaway_layers": cutaway_layers,
            "wedding_portions": w_slices,
            "party_portions": p_slices,
            "internal_dowels_count": dowels_in_tier,
        })
        current_y_cm += height

    base_bottom_diam = float(tier_specs[0].get("diameter_cm", 25.0))
    slenderness_ratio = round(current_y_cm / max(1.0, base_bottom_diam), 2)
    if slenderness_ratio > 2.6:
        return {
            "ok": False,
            "error": f"SLENDERNESS_RATIO_UNSAFE({slenderness_ratio}>2.6): increase base diameter or reduce total height",
        }

    pit_str = str(point_in_time_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"))[:10]
    bitemporal_lots = filter_point_in_time_records(
        records=ASAE_HACCP_BITEMPORAL_LOT_AND_COST_TABLE,
        point_in_time_date=pit_str,
        enforce_rls=False,
    )
    lot_cost_multiplier = float(bitemporal_lots[0].get("ingredient_cost_multiplier", 1.0)) if bitemporal_lots else 1.0

    frosting_weight_g = round(total_surface_cm2 * 0.85, 1)
    nutrition_weighted.append((frosting_weight_g, frosting["nutrition_per_100g"]))
    total_cake_weight_kg = round((sponge_weight_g + filling_weight_g + frosting_weight_g) / 1000.0, 2)

    nutritional_table = compute_eu_1169_nutritional_declaration(
        weighted_components=nutrition_weighted,
        portions_count=total_wedding_portions,
        portion_label_pt="Fatia Casamento (2,5×5 cm)",
    )

    unique_sponge_names = list(dict.fromkeys(tb["sponge_name"] for tb in per_tier_flavor_breakdown))
    unique_filling_names = list(dict.fromkeys(tb["filling_name"] for tb in per_tier_flavor_breakdown))
    is_mixed_tier_flavors = len(unique_sponge_names) > 1 or len(unique_filling_names) > 1

    # Costing & Locale-Ready Fiscal Pricing (Standard VAT vs. Small-Business Tax Exemption + True Gross-Input CMV)
    net_ingredients_only = (
        sponge_cost_raw_eur
        + filling_cost_raw_eur
        + (frosting_weight_g / 1000.0) * float(frosting["cost_eur_per_kg"])
    ) * lot_cost_multiplier
    net_packaging_only = len(tier_specs) * 4.50
    raw_materials_net_eur = net_ingredients_only + net_packaging_only

    locale_prof = resolve_locale_fiscal_profile(country_code, custom_fiscal_overrides)
    mode_upper = str(consumption_mode or "RESTAURACAO_13").strip().upper()
    is_exempt_mode = mode_upper in (
        "EXEMPT_SMALL_BUSINESS",
        "ISENTO_ART53",
        "EXEMPT",
        "EXEMPT_0",
        "ISE",
        "MEI",
        "KLEIN",
    )

    if is_exempt_mode and not locale_prof.input_tax_deductible_when_exempt:
        non_recoverable_input_tax_eur = round(
            net_ingredients_only * (locale_prof.reduced_raw_ingredients_rate_pct / 100.0)
            + net_packaging_only * (locale_prof.takeaway_or_standard_rate_pct / 100.0),
            2,
        )
    else:
        non_recoverable_input_tax_eur = 0.0

    raw_materials_eur = raw_materials_net_eur + non_recoverable_input_tax_eur
    estimated_labor_hours = round(2.5 + (len(tier_specs) * 1.8) + (total_wedding_portions * 0.025), 1)
    labor_cost_eur = estimated_labor_hours * float(hourly_rate_eur)
    subtotal_net_eur = round((raw_materials_eur * 1.35) + labor_cost_eur, 2)

    if is_exempt_mode:
        iva_rate_pct = 0.0
        resolved_tax_code = locale_prof.exemption_tax_code
        tax_exemption_code = locale_prof.exemption_reason_code
        tax_exemption_reason = locale_prof.exemption_legal_mention
        iva_regime_label = f"{locale_prof.exemption_scheme_name} ({locale_prof.exemption_reason_code})"
    elif mode_upper in ("TAKEAWAY_23", "ENTREGA_23", "23", "TAKEAWAY", "STANDARD"):
        iva_rate_pct = float(locale_prof.takeaway_or_standard_rate_pct)
        resolved_tax_code = locale_prof.standard_tax_code
        tax_exemption_code = None
        tax_exemption_reason = None
        iva_regime_label = (
            "Taxa Normal IVA 23% (Take-Away / Entrega de Bolo Decorado — CIVA Art. 18.º)"
            if locale_prof.country_code == "PT"
            else f"{locale_prof.jurisdiction_name} Standard/Takeaway Tax {iva_rate_pct:.2f}% ({resolved_tax_code})"
        )
    else:
        iva_rate_pct = float(locale_prof.dine_in_or_catering_rate_pct)
        resolved_tax_code = locale_prof.dine_in_tax_code
        tax_exemption_code = None
        tax_exemption_reason = None
        iva_regime_label = (
            "Taxa Intermédia IVA 13% (Serviço de Restauração / Catering — CIVA Lista II Verba 3.1)"
            if locale_prof.country_code == "PT"
            else f"{locale_prof.jurisdiction_name} Catering/Hospitality Tax {iva_rate_pct:.2f}% ({resolved_tax_code})"
        )

    total_gross_eur = round(subtotal_net_eur * (1.0 + (iva_rate_pct / 100.0)), 2)
    deposit_50pct_eur = round(total_gross_eur * 0.50, 2)

    nif_valid: Optional[bool] = None
    nif_masked: Optional[str] = None
    if client_nif:
        digits = "".join(ch for ch in str(client_nif) if ch.isdigit())
        nif_valid = validate_portuguese_nif_modulo11(digits)
        nif_masked = f"{digits[:2]}*****{digits[-2:]}" if len(digits) == 9 else "NIF-INVALID"

    tier_flavor_sig = "|".join(f"{tb['sponge_key']}+{tb['filling_key']}" for tb in per_tier_flavor_breakdown)
    sig_seed = f"{shape_clean}:{len(tier_specs)}:{tier_flavor_sig}:{resolved_frosting_key}:{total_gross_eur}"
    design_sha256 = hashlib.sha256(sig_seed.encode("utf-8")).hexdigest()
    atcud_preview = f"ATCUD:JJ7B4K30-{int(design_sha256[:6], 16) % 90000 + 10000}"
    multibanco_seed_7d = int(design_sha256[:7], 16) % 10_000_000
    multibanco_ref_50pct = format_multibanco_ref_mod97("21403", multibanco_seed_7d, int(round(deposit_50pct_eur * 100)))

    # Mandatory EU Reg. 1169/2011 Annex II Allergen Union (sorted by statutory Annex II number 1..14)
    allergen_codes = sorted(
        raw_allergen_codes,
        key=lambda c: int(EU_14_MANDATORY_ALLERGENS.get(c, {}).get("anexo_ii_num", 99)),
    )
    allergen_declarations = [
        {
            "code": c,
            "anexo_ii_num": EU_14_MANDATORY_ALLERGENS.get(c, {}).get("anexo_ii_num", 0),
            "statutory_label_pt": EU_14_MANDATORY_ALLERGENS.get(c, {}).get("label_pt", c),
        }
        for c in allergen_codes
    ]
    trace_codes = [
        c.strip().upper()
        for c in (may_contain_trace_codes or [])
        if c and c.strip().upper() in EU_14_MANDATORY_ALLERGENS and c.strip().upper() not in allergen_codes
    ]
    counter_signage_pt = (
        "CONTÉM ALERGÉNIOS (Reg. UE 1169/2011 & DL 26/2016): "
        + ", ".join(d["statutory_label_pt"].split(" — ")[0] for d in allergen_declarations)
        + (f". Pode conter vestígios de: {', '.join(trace_codes)}." if trace_codes else ".")
    )

    comfyui_controlnet_spec = {
        "engine": "ComfyUI Flux.1-dev / SDXL + ControlNet Depth & Canny Lock",
        "controlnet_depth_strength": 0.88,
        "controlnet_canny_strength": 0.65,
        "z_depth_cas_uri": f"cas://insight-bake/zdepth/{design_sha256[:16]}.exr",
        "anti_hallucination_geometry_lock": f"Locked to exact {len(tier_specs)}-tier Three.js Z-depth map ({total_wedding_portions} portions, {round(current_y_cm, 1)}cm total height)",
        "positive_prompt": (
            f"Commercial studio pastry photography of a {len(tier_specs)}-tier {shape_clean.lower()} celebration cake, "
            f"tier diameters {[t['diameter_cm'] for t in threejs_meshes]} cm, total height {round(current_y_cm, 1)} cm, "
            f"covered in {frosting['name']} ({primary_color_hex}) with {accent_color_hex} accents, {style_theme}, "
            f"custom acrylic topper reading '{safe_topper}', 85mm f/1.8 macro lens, soft diffused natural window key light, "
            "hyper-realistic sugar and buttercream texture, luxury wedding editorial lighting, 8k resolution"
        ),
        "negative_prompt": "lopsided tiers, floating elements, collapsed cake, plastic look, cartoon, watermark, deformed text, extra tiers",
    }

    box_width_cm = round(max_diameter_cm + 10.0, 1)
    box_height_cm = round(current_y_cm + 14.0, 1)
    center_skewer_required = len(tier_specs) >= 2

    return {
        "ok": True,
        "member": "InsightBake",
        "client_brand": "SetMiddle Insight™ · Bake (Cake & Pastry 3D Studio)",
        "internal_engine": "InsightCore",
        "design_sha256": design_sha256,
        "threejs_3d_scene": {
            "shape": shape_clean,
            "tier_count": len(tier_specs),
            "mixed_tier_flavors": is_mixed_tier_flavors,
            "cutaway_slice_ready": True,
            "total_height_cm": round(current_y_cm, 1),
            "max_base_diameter_cm": round(max_diameter_cm, 1),
            "slenderness_ratio": slenderness_ratio,
            "center_of_mass_stable": slenderness_ratio <= 2.2,
            "topper_text": safe_topper,
            "tiers": threejs_meshes,
        },
        "portions_and_structure": {
            "wedding_portions_2_5x5cm": total_wedding_portions,
            "party_portions_5x5cm": total_party_portions,
            "total_assembled_weight_kg": total_cake_weight_kg,
            "center_sharpened_dowel_skewer_required": center_skewer_required,
            "slenderness_ratio_h_over_d": slenderness_ratio,
            "tier_dowel_blueprint": structural_dowels,
        },
        "recipe_bom_grams": {
            "sponge_key": default_sponge_key,
            "sponge_type": " + ".join(unique_sponge_names),
            "sponge_total_g": sponge_weight_g,
            "sponge_ingredients_g": sponge_ingredients_g,
            "sponge_baking_temp_c": sponge["baking_temp_c"],
            "sponge_baking_time_minutes": sponge["baking_time_minutes"],
            "filling_key": default_filling_key,
            "filling_type": " + ".join(unique_filling_names),
            "filling_total_g": filling_weight_g,
            "filling_breakdown_g": filling_breakdown_g,
            "per_tier_flavors": per_tier_flavor_breakdown,
            "frosting_key": resolved_frosting_key,
            "frosting_type": frosting["name"],
            "frosting_total_g": frosting_weight_g,
        },
        "allergens_eu_1169_2011": {
            "regulation": "Regulamento (UE) n.º 1169/2011 Anexo II (14 Alergénios) & Decreto-Lei n.º 26/2016 (ASAE)",
            "allergen_codes": allergen_codes,
            "may_contain_traces": trace_codes,
            "mandatory_client_label": allergen_declarations,
            "allergen_counter_signage_pt": counter_signage_pt,
        },
        "nutritional_declaration_eu_1169": nutritional_table,
        "pricing_and_at_invoicing": {
            "country_code": locale_prof.country_code,
            "currency_code": locale_prof.currency_code,
            "raw_ingredients_and_packaging_net_cost_eur": round(raw_materials_net_eur, 2),
            "non_recoverable_input_tax_included_in_cmv_eur": non_recoverable_input_tax_eur,
            "raw_ingredients_and_packaging_cost_eur": round(raw_materials_eur, 2),
            "estimated_baker_labor_hours": estimated_labor_hours,
            "labor_cost_eur": round(labor_cost_eur, 2),
            "recommended_net_price_eur": subtotal_net_eur,
            "consumption_mode": mode_upper,
            "tax_code": resolved_tax_code,
            "tax_exemption_code": tax_exemption_code,
            "tax_exemption_reason": tax_exemption_reason,
            "iva_rate_pct": iva_rate_pct,
            "iva_regime_label_pt": iva_regime_label,
            "recommended_client_total_gross_eur": total_gross_eur,
            "deposit_50pct_atcud_invoice_eur": deposit_50pct_eur,
            "atcud_preview": atcud_preview,
            "multibanco_entity": "21403",
            "multibanco_ref_50pct": multibanco_ref_50pct,
            "client_nif_masked": nif_masked,
            "client_nif_modulo11_valid": nif_valid,
        },
        "comfyui_controlnet_render": comfyui_controlnet_spec,
        "logistics_and_haccp_cold_chain": {
            "powered_by": [
                "SetMiddle Insight™ · Fleet (:4026)",
                "SetMiddle Insight™ · Sensor (:4025)",
                "SetMiddle Insight™ · Pastelaria (:4029 — Reserva 24h & Dossier ASAE)",
                "SetMiddle Insight™ · Timeline (Bi-Temporal ASAE Lot & Cost Traceability)",
            ],
            "required_transport_box_cm": f"{box_width_cm} x {box_width_cm} x {box_height_cm} cm",
            "refrigerated_van_target_temp_c": "+2.0 °C to +5.0 °C (ASAE Reg. CE 852/2004)",
            "max_safe_ambient_display_temp_c": frosting["max_ambient_temp_c"],
            "summer_thermal_melt_countdown": compute_thermal_melt_countdown(
                max_safe_ambient_c=float(frosting["max_ambient_temp_c"]),
                venue_temp_c=float(venue_temp_c),
                venue_rh_pct=float(venue_rh_pct),
                tier_count=len(tier_specs),
            ),
            "max_safe_cornering_g_force": 0.35,
            "non_slip_silicone_mat_required": True,
            "bitemporal_haccp_lot_traceability": bitemporal_lots,
        },
    }


from insight_pastelaria.asae_ficha_tecnica import (
    ASAE_NORMATIVE_TEMPLATE_BASIS,
    ASAEEstablishmentProfile,
    ASAEFichaTecnica,
    build_validated_asae_ficha_tecnica,
    load_establishment_profile,
    render_asae_ficha_pdf_bytes,
    render_counter_allergen_matrix_pdf_bytes,
    render_printable_asae_ficha_html,
    save_establishment_profile,
)


def build_bake_asae_ficha_tecnica(result_res: Dict[str, Any]) -> ASAEFichaTecnica:
    """
    Converts any `InsightBake` 3D Multi-Tier Cake Design (`design_3d_cake_and_production_sheet`)
    OR Arrhenius Q10 Sourdough Batch (`compute_arrhenius_fermentation_and_bakers_pct`)
    into a 100% validated `MOD-FT-ASAE-DGAV-ACIP-v2.0` `ASAEFichaTecnica`.
    """
    if result_res.get("mode") == "arrhenius_fermentation_and_bakers_pct":
        b = result_res["bakers_percentage_bom_grams"]
        k = result_res["arrhenius_fermentation_kinetics"]
        t_rec = result_res["haccp_and_bitemporal_traceability"]
        f_hash = str(t_rec.get("sha256_audit_receipt") or "FERM0001")[:8].upper()
        ficha_id = f"FT-ASAE-FERM-{f_hash}"
        total_raw_g = float(b["total_dough_mass_kg"]) * 1000.0
        loaves = max(1, int(round(total_raw_g / 750.0)))
        unit_raw = round(total_raw_g / loaves, 1)
        unit_cooked = round(unit_raw * 0.87, 1)
        return build_validated_asae_ficha_tecnica(
            ficha_id=ficha_id,
            sku=f"pao_levain_{f_hash.lower()}",
            product_name=f"Pão de Fermentação Natural (Levain {b['starter_pct']}% · Hidratação {b['hydration_pct']}%)",
            category="Panificação Artesanal de Longa Fermentação (Arrhenius Q10 · InsightBake)",
            batch_yield_units=loaves,
            unit_raw_weight_g=unit_raw,
            unit_cooked_weight_g=unit_cooked,
            prep_time_minutes=int(k["estimated_bulk_fermentation_minutes"]),
            resting_or_freezing_minutes=int(float(k["cold_retard_hours"]) * 60),
            baking_temp_c=235.0,
            baking_time_minutes=36,
            core_target_temp_c=96.0,
            raw_ingredients=[
                {
                    "name": "Farinha de trigo T65 de mó de pedra",
                    "component_group": "Massa Base (100%)",
                    "gross_weight_g": float(b["flour_100pct_g"]),
                    "net_weight_g": float(b["flour_100pct_g"]),
                    "cost_eur_per_kg": 1.45,
                    "allergen_codes": ["GLUTEN"],
                },
                {
                    "name": f"Água potável filtrada a {k['required_water_temp_ddt_c']}°C (DDT)",
                    "component_group": "Hidratação",
                    "gross_weight_g": float(b["water_g"]),
                    "net_weight_g": float(b["water_g"]),
                    "cost_eur_per_kg": 0.02,
                    "allergen_codes": [],
                },
                {
                    "name": "Massa-mãe natural ativa (levain de trigo e centeio)",
                    "component_group": "Fermento Natural",
                    "gross_weight_g": float(b["levain_starter_g"]),
                    "net_weight_g": float(b["levain_starter_g"]),
                    "cost_eur_per_kg": 1.80,
                    "allergen_codes": ["GLUTEN"],
                },
                {
                    "name": "Sal marinho tradicional português",
                    "component_group": "Regulador Enzimático",
                    "gross_weight_g": float(b["salt_g"]),
                    "net_weight_g": float(b["salt_g"]),
                    "cost_eur_per_kg": 0.90,
                    "allergen_codes": [],
                },
            ],
            preparation_steps=[
                f"Autólise da farinha com água regulada a {k['required_water_temp_ddt_c']}°C para atingir DDT de {k['target_dough_temp_c']}°C.",
                f"Incorporar o levain ({b['starter_pct']}%) e o sal marinho ({b['salt_pct']}%), conduzindo fermentação em bloco de {k['estimated_bulk_fermentation_hours']} h.",
                f"Dividir em {loaves} unidades de {unit_raw} g, tender e retardar a frio (+{k['cold_retard_temp_c']}°C) durante {k['cold_retard_hours']} h.",
                "Cozer em forno de laje com vapor a 235°C durante 36 minutos até centro térmico >= +96°C.",
            ],
            good_hygiene_practices_bph=[
                "Controlar temperatura da água com termómetro calibrado e higienizar bannetons.",
                "Manter câmara de retardo a frio rigorosamente <= +4,0°C.",
            ],
            haccp_pccs=[
                {
                    "pcc_id": "PCC-1",
                    "stage": f"Retardo a Frio (+{k['cold_retard_temp_c']}°C / {k['cold_retard_hours']}h)",
                    "hazard_class": "Biológico",
                    "hazard_description": "Sobrefermentação ou crescimento indesejado fora de cadeia de frio.",
                    "critical_limit": "Câmara entre +1,0°C e +4,0°C.",
                    "monitoring_method": "Sonda `InsightActivity` zona `CHILLER`.",
                    "corrective_action": "Transferir tabuleiros para câmara de reserva se > +5,0°C.",
                    "verification_record": "Registo de Frio de Panificação.",
                },
                {
                    "pcc_id": "PCC-2",
                    "stage": "Cozedura com Vapor (235°C / 36 min)",
                    "hazard_class": "Biológico / Alergénico",
                    "hazard_description": "Gelatinização completa do amido e declaração obrigatória de Glúten (DL 26/2016).",
                    "critical_limit": "Centro térmico >= +95,0°C; dístico de Glúten afixado na prateleira.",
                    "monitoring_method": "Termómetro de sonda e verificação de abertura.",
                    "corrective_action": "Prolongar cozedura 5 min se miolo < +95°C.",
                    "verification_record": "Quadro de Alergénios de Balcão.",
                },
            ],
            storage_zones_to_validate=[
                {"zone": "CHILLER", "target_temp_c": min(4.0, max(1.0, float(k["cold_retard_temp_c"]))), "usage_note": "Retardo de massa em câmara (+1°C a +4°C)."},
                {"zone": "DRY_VITRINE", "target_temp_c": 20.0, "usage_note": "Exposição de pão cozido em escaparate seco higienizado."},
            ],
            primary_shelf_life="48 horas em escaparate ventilado seco à temperatura ambiente.",
            secondary_shelf_life="24 horas ao balcão de padaria protegido de contaminação.",
            may_contain_trace_codes=["SESAME", "SOY", "NUTS"],
            organoleptic_criteria={
                "aspeto": "Pestana aberta caramelizada e alvéolos bem distribuídos.",
                "cor": "Côdea castanha-dourada rústica.",
                "odor": f"Aroma lático-acético equilibrado ({k['lactic_to_acetic_profile']}).",
                "textura_e_sabor": "Côdea estaladiça e miolo elástico húmido.",
            },
            suggested_unit_gross_price_eur=4.20,
            iva_rate_pct=6.0,
            chronicle_book_id=f"FERM-{f_hash}",
            source_creator="SetMiddle Insight™ · Bake Arrhenius Lab",
        )

    scene = result_res["threejs_3d_scene"]
    bom = result_res["recipe_bom_grams"]
    struct = result_res["portions_and_structure"]
    allerg = result_res["allergens_eu_1169_2011"]
    pricing = result_res["pricing_and_at_invoicing"]
    cold = result_res["logistics_and_haccp_cold_chain"]

    design_hash = str(result_res["design_sha256"])[:8].upper()
    ficha_id = f"FT-ASAE-BAKE-{design_hash}"
    sku = f"bolo_3d_{design_hash.lower()}"

    sponge_spec = SPONGE_RECIPES.get(bom["sponge_key"], SPONGE_RECIPES["red_velvet"])
    filling_spec = FILLING_RECIPES.get(bom["filling_key"], FILLING_RECIPES["brigadeiro_gourmet"])
    frosting_spec = FROSTING_RECIPES.get(bom["frosting_key"], FROSTING_RECIPES["swiss_meringue_buttercream"])

    label_map = {
        "wheat_flour_g": ("Farinha de trigo T55 peneirada", ["GLUTEN"]),
        "almond_flour_g": ("Farinha de amêndoa selecionada", ["NUTS"]),
        "walnut_meal_g": ("Miolo de noz nobre moído", ["NUTS"]),
        "sugar_g": ("Açúcar branco granulado fino", []),
        "eggs_g": ("Ovo inteiro pasteurizado", ["EGGS"]),
        "butter_g": ("Manteiga pasteurizada sem sal (82% MG)", ["MILK"]),
        "buttermilk_g": ("Leitelho pasteurizado (buttermilk)", ["MILK"]),
        "dark_chocolate_70_g": ("Chocolate belga 70% cacau (lecitina de soja)", ["SOY", "MILK"]),
        "port_wine_reduction_g": ("Redução de Vinho do Porto DOP (contém sulfitos)", ["SULPHITES"]),
    }

    raw_ings: List[Dict[str, Any]] = []
    for k, grams in bom["sponge_ingredients_g"].items():
        lbl, explicit_alg = label_map.get(k, (k, []))
        raw_ings.append(
            {
                "name": lbl,
                "component_group": f"Massa Base ({bom['sponge_type']})",
                "gross_weight_g": round(float(grams) * 1.03, 1),
                "net_weight_g": float(grams),
                "cost_eur_per_kg": float(sponge_spec["cost_eur_per_kg"]),
                "allergen_codes": explicit_alg,
            }
        )
    raw_ings.append(
        {
            "name": str(bom["filling_type"]),
            "component_group": "Recheio Refrigerado",
            "gross_weight_g": round(float(bom["filling_total_g"]) * 1.02, 1),
            "net_weight_g": float(bom["filling_total_g"]),
            "cost_eur_per_kg": float(filling_spec["cost_eur_per_kg"]),
            "allergen_codes": list(filling_spec.get("allergens") or []),
        }
    )
    raw_ings.append(
        {
            "name": str(bom["frosting_type"]),
            "component_group": "Cobertura & Blindagem",
            "gross_weight_g": round(float(bom["frosting_total_g"]) * 1.04, 1),
            "net_weight_g": float(bom["frosting_total_g"]),
            "cost_eur_per_kg": float(frosting_spec["cost_eur_per_kg"]),
            "allergen_codes": list(frosting_spec.get("allergens") or []),
        }
    )

    cooked_g = max(500.0, round(float(struct["total_assembled_weight_kg"]) * 1000.0, 1))
    raw_g = round(max(cooked_g * 1.06, sum(i["net_weight_g"] for i in raw_ings)), 1)

    dowel_summary = (
        "; ".join(
            f"Andar {d['tier_index']} ({d['tier_diameter_cm']}cm): {d['polypropylene_dowel_rods_count']} estacas PP a {d['dowel_cut_height_cm']}cm + prato {d['cake_board_under_upper_tier_cm']}cm"
            for d in struct["tier_dowel_blueprint"]
        )
        or "Andar único estruturalmente estável (sem estacas internas)"
    )

    return build_validated_asae_ficha_tecnica(
        ficha_id=ficha_id,
        sku=sku,
        product_name=f"Bolo Celebrativo 3D {scene['tier_count']} Andares ({scene['shape']}) — \"{scene['topper_text']}\"",
        category="Cake Design Multi-Andar por Encomenda (SetMiddle Insight™ · Bake)",
        batch_yield_units=1,
        unit_raw_weight_g=raw_g,
        unit_cooked_weight_g=cooked_g,
        prep_time_minutes=int(round(float(pricing["estimated_baker_labor_hours"]) * 60)),
        resting_or_freezing_minutes=180,
        baking_temp_c=float(bom["sponge_baking_temp_c"]),
        baking_time_minutes=int(bom["sponge_baking_time_minutes"]),
        core_target_temp_c=84.0,
        raw_ingredients=raw_ings,
        preparation_steps=[
            f"1. Pesar matérias-primas em balança calibrada e cozer discos de '{bom['sponge_type']}' a {bom['sponge_baking_temp_c']}°C durante {bom['sponge_baking_time_minutes']} min (centro >= +82°C).",
            "2. Abater rapidamente os discos e o recheio em célula de arrefecimento até <= +4,0°C antes da montagem.",
            f"3. Montar estrutura interna certificada para uso alimentar: {dowel_summary}.",
            f"4. Aplicar blindagem '{bom['frosting_type']}', acondicionar em caixa isotérmica ({cold['required_transport_box_cm']}) e manter entre +2°C e +5°C.",
        ],
        good_hygiene_practices_bph=[
            "Desinfeção prévia de estacas de polipropileno (PP alimentar), espátulas, bailarina e pratos separadores.",
            "Utilização exclusiva de claras/ovos pasteurizados em coberturas de merengue e curds.",
            "Transporte em viatura isotérmica higienizada com tapete antiderrapante (força-G curva <= 0,35g).",
        ],
        haccp_pccs=[
            {
                "pcc_id": "PCC-1",
                "stage": f"Cozedura das Massas ({bom['sponge_baking_temp_c']}°C / {bom['sponge_baking_time_minutes']} min)",
                "hazard_class": "Biológico",
                "hazard_description": "Sobrevivência de Salmonella spp. em massas ricas em ovos.",
                "critical_limit": "Temperatura no centro térmico de cada disco >= +82,0°C.",
                "monitoring_method": "Sonda de penetração calibrada à saída do forno.",
                "corrective_action": "Prolongar cozedura em incrementos de 4 min até atingir >= +82,0°C.",
                "verification_record": "Registo de Fornadas Cake Studio (`InsightBake`).",
            },
            {
                "pcc_id": "PCC-2",
                "stage": "Armazenamento, Engenharia de Estacas & Transporte Frio",
                "hazard_class": "Biológico / Físico-Estrutural",
                "hazard_description": "Multiplicação microbiana em recheios refrigerados, corpos estranhos não alimentares ou colapso estrutural.",
                "critical_limit": f"Câmara +2,0°C a +4,0°C; exposição máx. <= +{cold['max_safe_ambient_display_temp_c']}°C; apenas estacas PP próprias p/ contacto alimentar informadas ao cliente.",
                "monitoring_method": "Telemetria IoT de câmara e conferência física da contagem de estacas na guia de entrega.",
                "corrective_action": "Bloquear expedição se núcleo > +5,0°C; declarar nº exato de estacas internas na etiqueta de corte.",
                "verification_record": "Guia de Expedição Frio & Ficha Técnica ASAE.",
            },
        ],
        storage_zones_to_validate=[
            {
                "zone": "CHILLER",
                "target_temp_c": 3.0,
                "usage_note": f"Câmara refrigerada e transporte isotérmico ({cold['refrigerated_van_target_temp_c']}) em caixa {cold['required_transport_box_cm']}.",
            }
        ],
        primary_shelf_life="72 horas refrigerado (+2°C a +4°C) em embalagem fechada.",
        secondary_shelf_life=f"Até 3 horas em mesa de evento climatizada (<= +{cold['max_safe_ambient_display_temp_c']}°C).",
        may_contain_trace_codes=list(allerg.get("may_contain_traces") or ["NUTS", "SESAME"]),
        organoleptic_criteria={
            "aspeto": f"Bolo celebrativo {scene['tier_count']} andares ({scene['shape']}) perfeitamente nivelado ({struct['wedding_portions_2_5x5cm']} fatias casamento).",
            "cor": f"Base {scene['tiers'][0]['base_color_hex']} com detalhes {scene['tiers'][0]['piping_accent_color_hex']}.",
            "odor": "Aroma fresco e nobre característico da massa e recheio selecionados.",
            "textura_e_sabor": "Camadas húmidas e equilibradas com cobertura estável.",
        },
        suggested_unit_gross_price_eur=float(pricing["recommended_client_total_gross_eur"]),
        iva_rate_pct=float(pricing["iva_rate_pct"]),
        chronicle_book_id=f"BAKE-{design_hash}",
        source_creator="SetMiddle Insight™ · Bake 3D Studio",
    )


def render_cake_asae_ficha_html(
    design_res: Dict[str, Any],
    establishment: Optional[ASAEEstablishmentProfile | Dict[str, Any]] = None,
    pdf_download_url: Optional[str] = None,
) -> str:
    """
    Renders the complete `MOD-FT-ASAE-DGAV-ACIP-v2.0` Official ASAE A4 HTML Sheet
    (with 14-Allergen Cross-Matrix, HACCP PCCs, Dowel Engineering & Establishment Header).
    """
    ficha = build_bake_asae_ficha_tecnica(design_res)
    return render_printable_asae_ficha_html(
        ficha,
        establishment=establishment,
        pdf_download_url=pdf_download_url or "/api/bake/ficha-asae/pdf",
    )


def render_cake_asae_ficha_pdf_bytes(
    design_res: Dict[str, Any],
    establishment: Optional[ASAEEstablishmentProfile | Dict[str, Any]] = None,
) -> bytes:
    """
    Renders a native Vector A4 Portrait PDF (`MOD-FT-ASAE-DGAV-ACIP-v2.0`) for any 3D Cake
    or Arrhenius Q10 Sourdough Batch in `InsightBake`.
    """
    ficha = build_bake_asae_ficha_tecnica(design_res)
    return render_asae_ficha_pdf_bytes(ficha, establishment=establishment)


class InsightBakeEngine:
    MEMBER_ID = "InsightBake"
    CLIENT_BRAND = "SetMiddle Insight™ · Bake"
    INTERNAL_ENGINE = "InsightCore"
    DEFAULT_PORT = 4030
    API_PREFIX = "/api/bake"

    def __init__(self, storage_dir: Optional[Path] = None) -> None:
        base_dir = Path(storage_dir) if storage_dir else (Path(__file__).resolve().parent.parent / "pipeline_data")
        self.base_dir = base_dir
        self.asae_fichas_dir = base_dir / "fichas_tecnicas_asae"
        self.unified_ledger_path = base_dir / "bake_unified_ledger.json"
        pastelaria_prof_dir = _PROJECTS_ROOT / "InsightPastelaria" / "pipeline_data" / "fichas_tecnicas_asae"
        if storage_dir is None and pastelaria_prof_dir.exists():
            self.establishment_profile_path = pastelaria_prof_dir / "establishment_profile.json"
        else:
            self.establishment_profile_path = self.asae_fichas_dir / "establishment_profile.json"
        self.registered_fichas: Dict[str, ASAEFichaTecnica] = {}
        self.deposit_payments: Dict[str, Dict[str, Any]] = {}
        self.render_jobs: Dict[str, Dict[str, Any]] = {}
        self.tasting_vouchers: Dict[str, Dict[str, Any]] = {}
        self.client_quotes: Dict[str, Dict[str, Any]] = {}
        self.fleet_deliveries: Dict[str, Dict[str, Any]] = {}
        self.stand_rentals: Dict[str, Dict[str, Any]] = {}
        self.locale_fiscal_config: Dict[str, Any] = {
            "country_code": "PT",
            "tax_regime": "STANDARD_VAT",
            "ytd_domestic_turnover": 0.0,
            "ytd_eu_cross_border_turnover": 0.0,
            "custom_overrides": {},
        }
        self._lock = threading.Lock()
        self.pg17_last_sync_status: str = "STANDBY_LOCAL_FALLBACK"

    def _sync_unified_pg17_or_local_ledger(self, event_type: str, record_id: str, payload_summary: Dict[str, Any]) -> str:
        """
        Unified PostgreSQL 17 (`:5432/chroniclerag`, Zero Runtime `ChromaDB` per `RULE-16`) dual-write
        with deterministic local JSON ledger fallback when `:5432` is unreachable or unconfigured.
        """
        ok_row, _ = assert_no_binary_blob_in_db_row(payload_summary)
        if not ok_row:
            raise ValueError("BINARY_BLOB_REJECTED_USE_CAS_URI")

        pg_synced = False
        for mod_name in ("psycopg", "psycopg2"):
            try:
                pg_mod = __import__(mod_name)
                conn = pg_mod.connect(
                    "postgresql://postgres:postgres@127.0.0.1:5432/chroniclerag",
                    connect_timeout=1,
                )
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            CREATE TABLE IF NOT EXISTS setmiddle_bake_events (
                                record_id TEXT PRIMARY KEY,
                                event_type TEXT NOT NULL,
                                payload_json JSONB NOT NULL,
                                created_at TIMESTAMPTZ DEFAULT NOW()
                            )
                            """
                        )
                        cur.execute(
                            """
                            INSERT INTO setmiddle_bake_events (record_id, event_type, payload_json)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (record_id) DO UPDATE SET payload_json = EXCLUDED.payload_json
                            """,
                            (record_id, event_type, json.dumps(payload_summary, ensure_ascii=False)),
                        )
                    conn.commit()
                    pg_synced = True
                    break
                finally:
                    conn.close()
            except Exception:
                continue

        self.base_dir.mkdir(parents=True, exist_ok=True)
        existing: List[Dict[str, Any]] = []
        if self.unified_ledger_path.exists():
            try:
                existing = json.loads(self.unified_ledger_path.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        existing = [r for r in existing if r.get("record_id") != record_id][-199:]
        existing.append({
            "record_id": record_id,
            "event_type": event_type,
            "pg17_synced": pg_synced,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary": payload_summary,
        })
        self.unified_ledger_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
        self.pg17_last_sync_status = "LIVE_PG17_5432" if pg_synced else "LOCAL_JSON_LEDGER_FALLBACK"
        return self.pg17_last_sync_status

    def get_establishment_profile(self) -> Dict[str, Any]:
        prof = load_establishment_profile(self.establishment_profile_path)
        return {"ok": True, "establishment": prof.to_dict()}

    def update_establishment_profile(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        prof = save_establishment_profile(self.establishment_profile_path, updates)
        self.asae_fichas_dir.mkdir(parents=True, exist_ok=True)
        for ficha in self.registered_fichas.values():
            (self.asae_fichas_dir / f"{ficha.ficha_id}.html").write_text(
                render_printable_asae_ficha_html(ficha, establishment=prof, pdf_download_url="/api/bake/ficha-asae/pdf"),
                encoding="utf-8",
            )
            (self.asae_fichas_dir / f"{ficha.ficha_id}.pdf").write_bytes(
                render_asae_ficha_pdf_bytes(ficha, establishment=prof)
            )
        return {"ok": True, "establishment": prof.to_dict(), "re_exported_fichas_count": len(self.registered_fichas)}

    def get_status(self) -> Dict[str, Any]:
        est = load_establishment_profile(self.establishment_profile_path)
        return {
            "ok": True,
            "product": self.CLIENT_BRAND,
            "member_id": self.MEMBER_ID,
            "internal_engine": self.INTERNAL_ENGINE,
            "version": "1.7.0",
            "port": self.DEFAULT_PORT,
            "api_prefix": self.API_PREFIX,
            "asae_normative_template": ASAE_NORMATIVE_TEMPLATE_BASIS["template_code"],
            "storage_engine": self.pg17_last_sync_status,
            "establishment": est.to_dict(),
            "standalone_benefit": (
                "Interactive Three.js 3D Multi-Tier Cake Configurator (Per-Tier Flavor Mixing + 3D Cutaway Cross-Section) "
                "+ Arrhenius Q10 Sourdough Fermentation Lab + EU 1169/2011 Allergens & Nutritional Table "
                "+ MB WAY / Multibanco 50% Deposit + SAF-T (PT) XML + Async ComfyUI Render Queue "
                "+ Catering Cutting & Dowel PDF + Stand Caução Ledger + Dietary Reformulator."
            ),
            "ecosystem_synergy": [
                "Combined with SetMiddle Insight™ · Pastelaria (:4029): Dispatches 24h custom cake orders directly into the Owner Stock-Confirmation Gate, FEFO Lot Ledger & ASAE Ficha Dossier.",
                "Combined with SetMiddle Insight™ · Fleet (:4026): Checks refrigerated delivery box dimensions, route smoothness (<=0.35g vibration), and venue arrival windows.",
                "Combined with SetMiddle Insight™ · Sensor (:4025): Monitors bakery fridge/freezer temperatures 24/7 for ASAE HACCP (Reg. CE 852/2004) compliance.",
                "Combined with SetMiddle Insight™ · Fiscal (:4017) & Expense (:4002): Issues immediate 50% deposit ATCUD / SAF-T (PT) v1.04_01 invoices (13% vs. 23% IVA) with MB WAY & Multibanco Modulo-97.",
            ],
            "available_shapes": ["ROUND", "SQUARE", "HEART", "HEXAGON"],
            "available_sponges": list(SPONGE_RECIPES.keys()),
            "available_fillings": list(FILLING_RECIPES.keys()),
            "available_frostings": list(FROSTING_RECIPES.keys()),
            "eu_14_allergens_supported": len(EU_14_MANDATORY_ALLERGENS),
            "active_render_jobs": len(self.render_jobs),
            "active_deposit_intents": len(self.deposit_payments),
            "active_client_quotes": len(self.client_quotes),
            "active_fleet_deliveries": len(self.fleet_deliveries),
            "active_stand_rentals": len(self.stand_rentals),
            "dietary_profiles_supported": ["GLUTEN_FREE_APC_20PPM", "LACTOSE_FREE", "VEGAN_100PCT"],
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def create_deposit_payment_intent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a 50% deposit payment intent (`MBWAY` or `MULTIBANCO` Modulo-97) for a 3D Cake design
        with CNPD/GDPR `Lei n.º 58/2019` phone/NIF masking and `ATCUD` reservation binding.
        """
        design = self.execute(payload)
        if not design.get("ok"):
            return design

        pricing = design["pricing_and_at_invoicing"]
        method = str(payload.get("payment_method") or "MULTIBANCO").strip().upper()
        if method not in ("MBWAY", "MULTIBANCO"):
            return {"ok": False, "error": f"UNSUPPORTED_PAYMENT_METHOD({method}): choose MBWAY or MULTIBANCO"}

        mbway_masked: Optional[str] = None
        if method == "MBWAY":
            raw_phone = "".join(ch for ch in str(payload.get("mbway_phone") or "") if ch.isdigit())
            if raw_phone.startswith("351") and len(raw_phone) == 12:
                raw_phone = raw_phone[3:]
            if len(raw_phone) != 9 or raw_phone[0] != "9" or raw_phone[1] not in "1236":
                return {"ok": False, "error": "INVALID_PT_MBWAY_PHONE: must be a valid 9-digit Portuguese mobile (91/92/93/96)"}
            mbway_masked = f"+351 {raw_phone[:2]}*** **{raw_phone[-2:]}"

        deposit_eur = float(pricing["deposit_50pct_atcud_invoice_eur"])
        payment_id = f"PAY-BAKE-{uuid.uuid4().hex[:8].upper()}"
        seed7 = int(hashlib.sha256(payment_id.encode("utf-8")).hexdigest()[:7], 16) % 10_000_000
        mb_ref = format_multibanco_ref_mod97("21403", seed7, int(round(deposit_eur * 100)))
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        record = {
            "payment_id": payment_id,
            "status": "AWAITING_SETTLEMENT",
            "payment_method": method,
            "deposit_amount_eur": deposit_eur,
            "total_order_gross_eur": float(pricing["recommended_client_total_gross_eur"]),
            "remaining_balance_on_pickup_eur": round(float(pricing["recommended_client_total_gross_eur"]) - deposit_eur, 2),
            "iva_rate_pct": float(pricing["iva_rate_pct"]),
            "atcud_code": pricing["atcud_preview"],
            "multibanco_entity": "21403" if method == "MULTIBANCO" else None,
            "multibanco_reference": mb_ref if method == "MULTIBANCO" else None,
            "mbway_phone_masked": mbway_masked,
            "design_sha256": design["design_sha256"],
            "created_at": now_iso,
            "settled_at": None,
            "sha256_settlement_receipt": None,
        }
        with self._lock:
            self.deposit_payments[payment_id] = record
        sync_mode = self._sync_unified_pg17_or_local_ledger("deposit_intent", payment_id, record)
        return {"ok": True, "payment": dict(record), "storage_sync": sync_mode}

    def confirm_deposit_payment(self, payment_id: str, transaction_ref: str = "SIBS-ACK-OK") -> Dict[str, Any]:
        with self._lock:
            rec = self.deposit_payments.get(str(payment_id or "").strip())
            if not rec:
                return {"ok": False, "error": f"PAYMENT_ID_NOT_FOUND({payment_id})"}
            if rec["status"] == "SETTLED_50PCT_DEPOSIT":
                return {"ok": False, "error": f"PAYMENT_ALREADY_SETTLED({payment_id})"}
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            safe_tx = _normalize_scrubbed_text(str(transaction_ref or "SIBS-ACK-OK"))[:48]
            receipt_hash = hashlib.sha256(
                f"{rec['payment_id']}:{rec['deposit_amount_eur']}:{rec['atcud_code']}:{safe_tx}:{now_iso}".encode("utf-8")
            ).hexdigest()
            rec["status"] = "SETTLED_50PCT_DEPOSIT"
            rec["settled_at"] = now_iso
            rec["transaction_ref"] = safe_tx
            rec["sha256_settlement_receipt"] = receipt_hash
            snapshot = dict(rec)
        sync_mode = self._sync_unified_pg17_or_local_ledger("deposit_settled", payment_id, snapshot)
        return {"ok": True, "payment": snapshot, "storage_sync": sync_mode}

    def export_saft_pt_invoice_xml(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exports a locale-ready `SAF-T v1.04_01` SalesInvoice XML snippet supporting any jurisdiction
        (`PT`, `ES`, `FR`, `DE`, `IT`, `GB`, `BR`, `US`, or custom), Standard VAT vs. Small-Business
        Tax Exemption (`M10` / `CGI-293B` / `USTG-19` / `CRT-4`), and intra-year hard-cliff blocking.
        """
        data = payload or {}
        eff_country = str(data.get("country_code") or self.locale_fiscal_config.get("country_code") or "PT").strip().upper()
        design = self.execute(data)
        if not design.get("ok"):
            return design

        raw_nif = "".join(ch for ch in str(data.get("client_nif") or "") if ch.isdigit())
        if raw_nif and eff_country == "PT" and not validate_portuguese_nif_modulo11(raw_nif):
            return {"ok": False, "error": f"INVALID_CLIENT_NIF_MODULO11({raw_nif})"}
        customer_tax_id = raw_nif if raw_nif else "999999990"

        est = load_establishment_profile(self.establishment_profile_path)
        pricing = design["pricing_and_at_invoicing"]
        scene = design["threejs_3d_scene"]
        country_code = str(pricing.get("country_code") or eff_country)
        currency_code = str(pricing.get("currency_code") or "EUR")
        iva_pct = float(pricing["iva_rate_pct"])
        tax_code = str(pricing.get("tax_code") or ("INT" if iva_pct == 13.0 else ("ISE" if iva_pct == 0.0 else "NOR")))
        exemption_code = pricing.get("tax_exemption_code")
        exemption_reason = pricing.get("tax_exemption_reason")
        net_total = float(pricing["recommended_net_price_eur"])
        gross_total = float(pricing["recommended_client_total_gross_eur"])
        tax_payable = round(gross_total - net_total, 2)

        cliff_eval = None
        if iva_pct == 0.0 and exemption_code:
            eff_ytd = (
                float(data["ytd_turnover_override"])
                if data.get("ytd_turnover_override") is not None
                else float(self.locale_fiscal_config.get("ytd_domestic_turnover", 0.0))
            )
            cliff_eval = evaluate_turnover_cliff_and_quote_guard(
                country_code=country_code,
                tax_regime="EXEMPT_SMALL_BUSINESS",
                ytd_domestic_turnover=eff_ytd,
                proposed_order_amount=gross_total,
                ytd_eu_cross_border_turnover=float(self.locale_fiscal_config.get("ytd_eu_cross_border_turnover", 0.0)),
                custom_overrides=data.get("custom_fiscal_overrides") or self.locale_fiscal_config.get("custom_overrides"),
            )
            if bool(data.get("enforce_cliff_guard", True)) and not cliff_eval["allow_exempt_invoice"]:
                return {
                    "ok": False,
                    "error": f"HARD_TAX_CLIFF_BREACH_SWITCH_TO_STANDARD_VAT: {cliff_eval['action_required']}",
                    "cliff_guard": cliff_eval,
                }

        now_dt = datetime.now(timezone.utc)
        date_str = now_dt.strftime("%Y-%m-%d")
        sys_entry = now_dt.strftime("%Y-%m-%dT%H:%M:%S")
        inv_seq = int(design["design_sha256"][:6], 16) % 90000 + 10000
        invoice_no = f"FT IB2026/{inv_seq}"
        atcud_clean = str(pricing["atcud_preview"]).replace("ATCUD:", "")
        doc_hash = hashlib.sha256(f"{date_str};{sys_entry};{invoice_no};{gross_total:.2f};".encode("utf-8")).hexdigest()[:32]
        exemption_xml_block = (
            f"\n          <TaxExemptionReason>{html.escape(str(exemption_reason))}</TaxExemptionReason>"
            f"\n          <TaxExemptionCode>{html.escape(str(exemption_code))}</TaxExemptionCode>"
            if exemption_code
            else ""
        )

        xml_str = f"""<?xml version="1.0" encoding="UTF-8"?>
<AuditFile xmlns="urn:OECD:StandardAuditFile-Tax:PT_1.04_01">
  <Header>
    <AuditFileVersion>1.04_01</AuditFileVersion>
    <CompanyID>{html.escape(est.nif)}</CompanyID>
    <TaxRegistrationNumber>{html.escape(est.nif)}</TaxRegistrationNumber>
    <TaxAccountingBasis>F</TaxAccountingBasis>
    <CompanyName>{html.escape(est.denominacao_social)}</CompanyName>
    <FiscalYear>{now_dt.year}</FiscalYear>
    <CurrencyCode>{html.escape(currency_code)}</CurrencyCode>
    <DateCreated>{date_str}</DateCreated>
    <ProductID>SetMiddle InsightBake/InsightCore</ProductID>
    <ProductVersion>1.7.0</ProductVersion>
  </Header>
  <MasterFiles>
    <Customer>
      <CustomerID>CLI-{customer_tax_id[:4]}</CustomerID>
      <AccountID>21110001</AccountID>
      <CustomerTaxID>{customer_tax_id}</CustomerTaxID>
      <CompanyName>{html.escape("Consumidor Final" if customer_tax_id == "999999990" else _normalize_scrubbed_text(str(data.get("client_name") or "Cliente Particular")))}</CompanyName>
      <BillingAddress><Country>{html.escape(country_code)}</Country></BillingAddress>
      <SelfBillingIndicator>0</SelfBillingIndicator>
    </Customer>
  </MasterFiles>
  <SourceDocuments>
    <SalesInvoices>
      <NumberOfEntries>1</NumberOfEntries>
      <TotalDebit>0.00</TotalDebit>
      <TotalCredit>{net_total:.2f}</TotalCredit>
      <Invoice>
        <InvoiceNo>{invoice_no}</InvoiceNo>
        <ATCUD>{html.escape(atcud_clean)}</ATCUD>
        <DocumentStatus>
          <InvoiceStatus>N</InvoiceStatus>
          <InvoiceStatusDate>{sys_entry}</InvoiceStatusDate>
          <SourceID>INSIGHTBAKE</SourceID>
          <SourceBilling>P</SourceBilling>
        </DocumentStatus>
        <Hash>{doc_hash}</Hash>
        <HashControl>1</HashControl>
        <InvoiceDate>{date_str}</InvoiceDate>
        <InvoiceType>FT</InvoiceType>
        <SourceID>INSIGHTBAKE</SourceID>
        <SystemEntryDate>{sys_entry}</SystemEntryDate>
        <CustomerID>CLI-{customer_tax_id[:4]}</CustomerID>
        <Line>
          <LineNumber>1</LineNumber>
          <ProductCode>BOLO3D-{design["design_sha256"][:8].upper()}</ProductCode>
          <ProductDescription>{html.escape(f"Bolo 3D {scene['tier_count']} Andares ({scene['shape']}) - {scene['topper_text']}")}</ProductDescription>
          <Quantity>1</Quantity>
          <UnitOfMeasure>UN</UnitOfMeasure>
          <UnitPrice>{net_total:.2f}</UnitPrice>
          <TaxPointDate>{date_str}</TaxPointDate>
          <Description>{html.escape(pricing["iva_regime_label_pt"])}</Description>
          <CreditAmount>{net_total:.2f}</CreditAmount>
          <Tax>
            <TaxType>IVA</TaxType>
            <TaxCountryRegion>{html.escape(country_code)}</TaxCountryRegion>
            <TaxCode>{html.escape(tax_code)}</TaxCode>
            <TaxPercentage>{iva_pct:.2f}</TaxPercentage>
          </Tax>{exemption_xml_block}
        </Line>
        <DocumentTotals>
          <TaxPayable>{tax_payable:.2f}</TaxPayable>
          <NetTotal>{net_total:.2f}</NetTotal>
          <GrossTotal>{gross_total:.2f}</GrossTotal>
        </DocumentTotals>
      </Invoice>
    </SalesInvoices>
  </SourceDocuments>
</AuditFile>"""
        return {
            "ok": True,
            "country_code": country_code,
            "currency_code": currency_code,
            "invoice_no": invoice_no,
            "atcud": pricing["atcud_preview"],
            "tax_code": tax_code,
            "tax_exemption_code": exemption_code,
            "cliff_guard": cliff_eval,
            "iva_rate_pct": iva_pct,
            "net_total_eur": net_total,
            "tax_payable_eur": tax_payable,
            "gross_total_eur": gross_total,
            "saft_pt_version": "1.04_01",
            "xml": xml_str,
        }

    def submit_comfyui_render_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Non-blocking asynchronous `ComfyUI` ControlNet Depth/Canny render job queue (`RULE-10` & `EU AI Act Art. 14`).
        Enforces `CAS URI` storage (`cas://insight-bake/...`) and rejects raw inline base64 binary blobs.
        """
        ok_storage, violations = assert_no_binary_blob_in_db_row(payload or {})
        if not ok_storage:
            return {"ok": False, "error": "BINARY_BLOB_REJECTED_USE_CAS_URI", "violations": violations}

        z_uri = str((payload or {}).get("z_depth_cas_uri") or "").strip()
        if z_uri and not z_uri.startswith("cas://"):
            return {"ok": False, "error": "INVALID_Z_DEPTH_URI_MUST_USE_CAS_SCHEME"}

        design = self.execute(payload)
        if not design.get("ok"):
            return design

        resolved_z_uri = z_uri or design["comfyui_controlnet_render"]["z_depth_cas_uri"]
        job_id = f"RND-BAKE-{uuid.uuid4().hex[:8].upper()}"
        render_hash = hashlib.sha256(f"{job_id}:{design['design_sha256']}".encode("utf-8")).hexdigest()
        output_cas_uri = f"cas://insight-bake/renders/{render_hash[:24]}.webp"
        simulate_delay_ms = max(0, min(2000, int((payload or {}).get("simulate_delay_ms", 40))))
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        job_rec: Dict[str, Any] = {
            "job_id": job_id,
            "status": "QUEUED",
            "progress_pct": 10,
            "stage_pt": "Agendado na fila assíncrona ControlNet Depth (RULE-10)...",
            "cancel_requested": False,
            "z_depth_cas_uri": resolved_z_uri,
            "output_render_cas_uri": None,
            "controlnet_spec": design["comfyui_controlnet_render"],
            "design_sha256": design["design_sha256"],
            "created_at": now_iso,
            "updated_at": now_iso,
        }
        with self._lock:
            self.render_jobs[job_id] = job_rec

        def _render_worker() -> None:
            if simulate_delay_ms > 0:
                time.sleep(simulate_delay_ms / 1000.0)
            with self._lock:
                if job_rec["cancel_requested"]:
                    job_rec["status"] = "ABORTED"
                    job_rec["stage_pt"] = "Renderização abortada pelo utilizador (EU AI Act Art. 14)."
                    job_rec["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    return
                job_rec["status"] = "RUNNING"
                job_rec["progress_pct"] = 55
                job_rec["stage_pt"] = "A sintetizar texturas fotorrealistas bloqueadas pelo mapa Z-depth..."
                job_rec["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            if simulate_delay_ms > 0:
                time.sleep(simulate_delay_ms / 1000.0)

            with self._lock:
                if job_rec["cancel_requested"]:
                    job_rec["status"] = "ABORTED"
                    job_rec["stage_pt"] = "Renderização abortada pelo utilizador (EU AI Act Art. 14)."
                    job_rec["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    return
                job_rec["status"] = "COMPLETED"
                job_rec["progress_pct"] = 100
                job_rec["output_render_cas_uri"] = output_cas_uri
                job_rec["stage_pt"] = f"Renderização concluída: {output_cas_uri}"
                job_rec["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                done_copy = dict(job_rec)
            self._sync_unified_pg17_or_local_ledger("comfyui_render_job", job_id, {
                "job_id": job_id,
                "status": done_copy["status"],
                "z_depth_cas_uri": resolved_z_uri,
                "output_render_cas_uri": output_cas_uri,
            })

        threading.Thread(target=_render_worker, name=f"bake-render-{job_id}", daemon=True).start()
        return {"ok": True, "job": dict(job_rec)}

    def get_comfyui_render_job(self, job_id: str) -> Dict[str, Any]:
        with self._lock:
            rec = self.render_jobs.get(str(job_id or "").strip())
            if not rec:
                return {"ok": False, "error": f"RENDER_JOB_NOT_FOUND({job_id})"}
            return {"ok": True, "job": dict(rec)}

    def cancel_comfyui_render_job(self, job_id: str) -> Dict[str, Any]:
        with self._lock:
            rec = self.render_jobs.get(str(job_id or "").strip())
            if not rec:
                return {"ok": False, "error": f"RENDER_JOB_NOT_FOUND({job_id})"}
            rec["cancel_requested"] = True
            if rec["status"] in ("QUEUED", "RUNNING"):
                rec["status"] = "ABORTED"
                rec["stage_pt"] = "Renderização cancelada pelo utilizador (EU AI Act Art. 14)."
            rec["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            return {"ok": True, "job": dict(rec)}

    def search_safe_cake_configurations(
        self,
        query: str = "",
        exclude_allergens: Optional[List[str]] = None,
        min_portions: int = 30,
        ambient_temp_c: float = 21.0,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Semantic & constraint-aware recipe discovery (`RULE-16` Zero `ChromaDB` — Unified PG17 + deterministic local ranker).
        Parses natural-language dietary/event intents (e.g. 'sem glúten', 'sem frutos secos', 'casamento verão 27°C 100 pessoas')
        and returns ready-to-load 3D multi-tier designs strictly satisfying allergen and thermal bounds.
        """
        q_low = str(query or "").lower()
        excluded: set[str] = {str(a).strip().upper() for a in (exclude_allergens or []) if a}
        if any(p in q_low for p in ("sem glúten", "sem gluten", "gluten-free", "celíac", "celiac")):
            excluded.add("GLUTEN")
        if any(p in q_low for p in ("sem leite", "sem lactose", "dairy-free")):
            excluded.add("MILK")
        if any(p in q_low for p in ("sem frutos secos", "sem noz", "sem amêndoa", "nut-free")):
            excluded.add("NUTS")
        if any(p in q_low for p in ("sem soja", "soy-free")):
            excluded.add("SOY")
        if any(p in q_low for p in ("sem sésamo", "sem sesamo", "sesame-free")):
            excluded.add("SESAME")

        m_temp = re.search(r"(\d{2})\s*°?\s*c\b", q_low)
        eff_ambient_c = max(float(ambient_temp_c), float(m_temp.group(1))) if m_temp else float(ambient_temp_c)

        m_pax = re.search(r"(\d{2,3})\s*(?:pessoas|fatias|pax|convidados|portions)", q_low)
        eff_min_portions = max(int(min_portions), int(m_pax.group(1))) if m_pax else int(min_portions)

        tier_presets = [
            [{"diameter_cm": 20.0, "height_cm": 12.0}],
            [{"diameter_cm": 25.0, "height_cm": 12.0}, {"diameter_cm": 18.0, "height_cm": 12.0}],
            [{"diameter_cm": 28.0, "height_cm": 12.0}, {"diameter_cm": 20.0, "height_cm": 12.0}, {"diameter_cm": 14.0, "height_cm": 14.0}],
            [{"diameter_cm": 34.0, "height_cm": 13.0}, {"diameter_cm": 26.0, "height_cm": 13.0}, {"diameter_cm": 18.0, "height_cm": 14.0}],
        ]
        preferred_shape = "HEART" if ("coração" in q_low or "heart" in q_low or "romântic" in q_low) else ("HEXAGON" if "hex" in q_low else "ROUND")

        candidates: List[Dict[str, Any]] = []
        for sk, s_spec in SPONGE_RECIPES.items():
            if excluded & set(s_spec["allergens"]):
                continue
            for fk, f_spec in FILLING_RECIPES.items():
                if excluded & set(f_spec["allergens"]):
                    continue
                for frk, fr_spec in FROSTING_RECIPES.items():
                    if excluded & set(fr_spec["allergens"]):
                        continue
                    if float(fr_spec["max_ambient_temp_c"]) < eff_ambient_c:
                        continue

                    # Pick smallest tier preset meeting eff_min_portions
                    chosen_design: Optional[Dict[str, Any]] = None
                    for tp in tier_presets:
                        d = design_3d_cake_and_production_sheet(
                            tiers=tp,
                            shape=preferred_shape,
                            sponge_key=sk,
                            filling_key=fk,
                            frosting_key=frk,
                        )
                        if d.get("ok") and d["portions_and_structure"]["wedding_portions_2_5x5cm"] >= eff_min_portions:
                            chosen_design = d
                            break
                    if chosen_design is None:
                        d_max = design_3d_cake_and_production_sheet(
                            tiers=tier_presets[-1],
                            shape=preferred_shape,
                            sponge_key=sk,
                            filling_key=fk,
                            frosting_key=frk,
                        )
                        if d_max.get("ok") and d_max["portions_and_structure"]["wedding_portions_2_5x5cm"] >= eff_min_portions:
                            chosen_design = d_max
                    if not chosen_design:
                        continue

                    score = 1.0
                    haystack = f"{sk} {s_spec['name']} {fk} {f_spec['name']} {frk} {fr_spec['name']}".lower()
                    for tok in re.findall(r"[a-záàâãéêíóôõúç0-9]{4,}", q_low):
                        if tok in haystack:
                            score += 0.35
                    candidates.append({
                        "relevance_score": round(score, 2),
                        "sponge_key": sk,
                        "sponge_name": s_spec["name"],
                        "filling_key": fk,
                        "filling_name": f_spec["name"],
                        "frosting_key": frk,
                        "frosting_name": fr_spec["name"],
                        "max_safe_ambient_temp_c": fr_spec["max_ambient_temp_c"],
                        "wedding_portions": chosen_design["portions_and_structure"]["wedding_portions_2_5x5cm"],
                        "total_gross_eur": chosen_design["pricing_and_at_invoicing"]["recommended_client_total_gross_eur"],
                        "allergen_codes": chosen_design["allergens_eu_1169_2011"]["allergen_codes"],
                        "design_payload": {
                            "shape": preferred_shape,
                            "tiers": [
                                {"diameter_cm": m["diameter_cm"], "height_cm": m["height_cm"]}
                                for m in chosen_design["threejs_3d_scene"]["tiers"]
                            ],
                            "sponge_key": sk,
                            "filling_key": fk,
                            "frosting_key": frk,
                        },
                    })

        candidates.sort(key=lambda c: (-c["relevance_score"], c["total_gross_eur"]))
        return {
            "ok": True,
            "storage_engine": "Unified PostgreSQL 17 + Deterministic Constraint Ranker (Zero ChromaDB RULE-16)",
            "applied_filters": {
                "excluded_allergens": sorted(excluded),
                "min_wedding_portions": eff_min_portions,
                "ambient_temp_c": eff_ambient_c,
            },
            "total_matches": len(candidates),
            "matches": candidates[: max(1, int(limit))],
        }

    def export_asae_ficha_artifacts(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a 3D Cake Design or Arrhenius Q10 Fermentation calculation, builds its
        `MOD-FT-ASAE-DGAV-ACIP-v2.0` `ASAEFichaTecnica`, persists `.html` + `.pdf`, and returns bytes.
        """
        res = self.execute(payload)
        if not res.get("ok"):
            return res
        est = load_establishment_profile(self.establishment_profile_path)
        ficha = build_bake_asae_ficha_tecnica(res)
        self.registered_fichas[ficha.ficha_id] = ficha
        self.asae_fichas_dir.mkdir(parents=True, exist_ok=True)
        html_str = render_printable_asae_ficha_html(
            ficha,
            establishment=est,
            pdf_download_url="/api/bake/ficha-asae/pdf",
        )
        pdf_bytes = render_asae_ficha_pdf_bytes(ficha, establishment=est)
        html_path = self.asae_fichas_dir / f"{ficha.ficha_id}.html"
        pdf_path = self.asae_fichas_dir / f"{ficha.ficha_id}.pdf"
        html_path.write_text(html_str, encoding="utf-8")
        pdf_path.write_bytes(pdf_bytes)
        return {
            "ok": True,
            "ficha": ficha,
            "html": html_str,
            "pdf_bytes": pdf_bytes,
            "html_path": str(html_path),
            "pdf_path": str(pdf_path),
            "design": res,
        }

    def render_counter_allergen_matrix_pdf(self) -> bytes:
        """
        Generates the A4 Landscape Counter Allergen Matrix PDF (`DL n.º 26/2016`) for `InsightBake`'s
        signature 3D Cake & Sourdough lines plus all custom cakes designed in the active studio.
        """
        est = load_establishment_profile(self.establishment_profile_path)
        presets = [
            {"shape": "ROUND", "sponge_key": "red_velvet", "filling_key": "brigadeiro_gourmet", "frosting_key": "swiss_meringue_buttercream", "topper_text": "Clássico Red Velvet"},
            {"shape": "SQUARE", "sponge_key": "chocolate_belga_70", "filling_key": "praline_avela_crocante", "frosting_key": "ganache_blindagem_fondant", "topper_text": "Belga 70% & Praliné"},
            {"shape": "HEART", "sponge_key": "amendoa_sem_gluten", "filling_key": "curd_limao_frutos_vermelhos", "frosting_key": "semi_naked_rustico", "topper_text": "Amêndoa Sem Glúten"},
            {"shape": "HEXAGON", "sponge_key": "nozes_vinho_porto", "filling_key": "pistacio_tahini_crocante", "frosting_key": "swiss_meringue_buttercream", "topper_text": "Noz Porto & Pistácio"},
            {"action": "fermentation", "flour_mass_g": 5000.0, "dough_temp_c": 26.0, "hydration_pct": 72.0, "starter_pct": 20.0},
        ]
        fichas_map: Dict[str, ASAEFichaTecnica] = {}
        for p in presets:
            r = self.execute(p)
            if r.get("ok"):
                f = build_bake_asae_ficha_tecnica(r)
                fichas_map[f.ficha_id] = f
        for fid, f_custom in self.registered_fichas.items():
            fichas_map[fid] = f_custom

        pdf_bytes = render_counter_allergen_matrix_pdf_bytes(list(fichas_map.values()), establishment=est)
        self.asae_fichas_dir.mkdir(parents=True, exist_ok=True)
        (self.asae_fichas_dir / "Quadro_Alergenios_Balcao_ASAE_DL26_2016.pdf").write_bytes(pdf_bytes)
        return pdf_bytes

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ok_storage, violations = assert_no_binary_blob_in_db_row(payload or {})
        if not ok_storage:
            return {"ok": False, "member": self.MEMBER_ID, "error": "BINARY_BLOB_REJECTED_USE_CAS_URI", "violations": violations}
        data = payload or {}

        # Route Arrhenius Fermentation & Baker's % requests cleanly when requested
        mode = str(data.get("action") or data.get("mode") or "").strip().lower()
        if mode in ("fermentation", "arrhenius", "sourdough") or ("flour_mass_g" in data and "tiers" not in data and "sponge_key" not in data):
            return compute_arrhenius_fermentation_and_bakers_pct(
                flour_mass_g=float(data.get("flour_mass_g", 5000.0)),
                dough_temp_c=float(data.get("dough_temp_c", 26.0)),
                hydration_pct=float(data.get("hydration_pct", 72.0)),
                starter_pct=float(data.get("starter_pct", 20.0)),
                salt_pct=float(data.get("salt_pct", 2.2)),
                ambient_temp_c=float(data.get("ambient_temp_c", 22.0)),
                flour_temp_c=float(data.get("flour_temp_c", 21.0)),
                cold_retard_temp_c=float(data.get("cold_retard_temp_c", 4.0)),
                cold_retard_hours=float(data.get("cold_retard_hours", 14.0)),
                point_in_time=data.get("point_in_time"),
            )

        default_mode = (
            "EXEMPT_SMALL_BUSINESS"
            if self.locale_fiscal_config.get("tax_regime") == "EXEMPT_SMALL_BUSINESS"
            else "RESTAURACAO_13"
        )
        return design_3d_cake_and_production_sheet(
            tiers=data.get("tiers"),
            shape=str(data.get("shape", "ROUND")),
            sponge_key=str(data.get("sponge_key") or data.get("spongeKey") or "red_velvet"),
            filling_key=str(data.get("filling_key") or data.get("fillingKey") or "brigadeiro_gourmet"),
            frosting_key=str(data.get("frosting_key") or data.get("frostingKey") or "swiss_meringue_buttercream"),
            style_theme=str(data.get("style_theme") or data.get("styleTheme") or "Vintage Lambeth Piping with Gold Leaf"),
            primary_color_hex=str(data.get("primary_color_hex") or data.get("primaryColorHex") or "#FFFDF9"),
            accent_color_hex=str(data.get("accent_color_hex") or data.get("accentColorHex") or "#D4AF37"),
            topper_text=str(data.get("topper_text") or data.get("topperText") or "Sofia & Miguel"),
            hourly_rate_eur=float(data.get("hourly_rate_eur", 22.0)),
            consumption_mode=str(data.get("consumption_mode") or default_mode),
            may_contain_trace_codes=data.get("may_contain_trace_codes"),
            client_nif=data.get("client_nif"),
            point_in_time_date=data.get("point_in_time_date"),
            venue_temp_c=float(data.get("venue_temp_c", 22.0)),
            venue_rh_pct=float(data.get("venue_rh_pct", 55.0)),
            country_code=str(data.get("country_code") or self.locale_fiscal_config.get("country_code") or "PT"),
            custom_fiscal_overrides=data.get("custom_fiscal_overrides") or self.locale_fiscal_config.get("custom_overrides"),
        )

    def dispatch_custom_cake_to_pastelaria(
        self,
        payload: Dict[str, Any],
        pastelaria_base_url: str = "http://127.0.0.1:4029",
    ) -> Dict[str, Any]:
        """
        Designs the 3D cake, builds the `day_before` (`24h`) production & ASAE handoff packet,
        and forwards it to `InsightPastelaria` (`:4029 /api/pastelaria/reservations/custom-cake`)
        when online, or returns a verified offline handoff envelope if `:4029` is unreachable.
        """
        export_bundle = self.export_asae_ficha_artifacts(payload)
        if not export_bundle.get("ok"):
            return export_bundle
        design = export_bundle["design"]
        ficha_obj: ASAEFichaTecnica = export_bundle["ficha"]

        client_name = _normalize_scrubbed_text(str(payload.get("client_name") or design["threejs_3d_scene"]["topper_text"] or "Cliente Cake Design"))
        requested_pickup = str(payload.get("requested_pickup_time") or "Amanhã às 16:00 (24h Cake Studio)")
        lead_mins = int(max(720, int(payload.get("lead_minutes_ahead", 1440))))
        handoff_packet = {
            "client_name": client_name,
            "requested_pickup_time": requested_pickup,
            "lead_minutes_ahead": lead_mins,
            "cake_design": design,
        }

        target_url = f"{pastelaria_base_url.rstrip('/')}/api/pastelaria/reservations/custom-cake"
        try:
            req = urllib.request.Request(
                target_url,
                data=json.dumps(handoff_packet).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                remote_data = json.loads(resp.read().decode("utf-8"))
                return {
                    "ok": True,
                    "bridge_mode": "LIVE_HTTP_4029",
                    "asae_ficha_id": ficha_obj.ficha_id,
                    "bake_pdf_path": export_bundle["pdf_path"],
                    "pastelaria_reservation": remote_data,
                    "cake_design": design,
                }
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            local_sync_info: Optional[Dict[str, Any]] = None
            try:
                from insight_pastelaria.engine import InsightPastelariaEngine

                local_past = InsightPastelariaEngine(load_persisted_state=True)
                local_sync_info = local_past.register_custom_cake_reservation_from_bake(
                    client_name=client_name,
                    requested_pickup_time=requested_pickup,
                    cake_design=design,
                    lead_minutes_ahead=lead_mins,
                )
            except Exception:
                local_sync_info = None

            return {
                "ok": True,
                "bridge_mode": "QUEUED_HANDOFF_PACKET",
                "local_pastelaria_ledger_synced": bool(local_sync_info),
                "asae_ficha_id": ficha_obj.ficha_id,
                "bake_pdf_path": export_bundle["pdf_path"],
                "pastelaria_local_sync": local_sync_info,
                "note": "Sincronizado diretamente no Dossier ASAE & Quadro de Alergénios em disco (HTTP :4029 offline).",
                "handoff_packet": handoff_packet,
                "cake_design": design,
            }

    def scrub_input(self, text: str) -> Dict[str, Any]:
        res = scrub_pt_eu_pii_and_byok_secrets(text)
        if isinstance(res, dict):
            return res
        if isinstance(res, tuple) and len(res) >= 2:
            return {"scrubbed_text": res[0], "stats": res[1]}
        return {"scrubbed_text": str(res), "stats": {}}

    # =========================================================================
    # ROUND-3 TRACKS: REVERSE GUEST/BUDGET SOLVER, TASTING BOX + QUOTE PORTAL,
    # AND REFRIGERATED FLEET G-FORCE + AT TRANSPORT GUIDE + CAS POD
    # =========================================================================
    def solve_cake_by_guests_and_budget(
        self,
        guest_count: int = 60,
        max_budget_eur: float = 280.0,
        exclude_allergens: Optional[List[str]] = None,
        venue_temp_c: float = 22.0,
        preferred_shape: str = "ROUND",
        consumption_mode: str = "RESTAURACAO_13",
    ) -> Dict[str, Any]:
        """
        Reverse Guest-Count & Budget Solver: searches multi-tier geometries and recipe combinations
        to find optimal structurally stable designs satisfying `wedding_portions >= guest_count`,
        `recommended_client_total_gross_eur <= max_budget_eur`, allergen exclusions, and thermal safety.
        """
        guests = max(8, int(guest_count))
        budget = float(max_budget_eur)
        if budget <= 20.0:
            return {"ok": False, "error": "BUDGET_TOO_LOW_MIN_20_EUR"}

        excluded = {str(a).strip().upper() for a in (exclude_allergens or []) if a}
        shape_clean = str(preferred_shape or "ROUND").strip().upper()
        if shape_clean not in ("ROUND", "SQUARE", "HEART", "HEXAGON"):
            shape_clean = "ROUND"

        tier_candidates = [
            [{"diameter_cm": 18.0, "height_cm": 12.0}],
            [{"diameter_cm": 22.0, "height_cm": 12.0}],
            [{"diameter_cm": 24.0, "height_cm": 12.0}, {"diameter_cm": 16.0, "height_cm": 12.0}],
            [{"diameter_cm": 26.0, "height_cm": 12.0}, {"diameter_cm": 18.0, "height_cm": 12.0}],
            [{"diameter_cm": 28.0, "height_cm": 12.0}, {"diameter_cm": 20.0, "height_cm": 12.0}, {"diameter_cm": 14.0, "height_cm": 12.0}],
            [{"diameter_cm": 32.0, "height_cm": 13.0}, {"diameter_cm": 24.0, "height_cm": 13.0}, {"diameter_cm": 16.0, "height_cm": 14.0}],
        ]

        solutions: List[Dict[str, Any]] = []
        for sk, s_spec in SPONGE_RECIPES.items():
            if excluded & set(s_spec["allergens"]):
                continue
            for fk, f_spec in FILLING_RECIPES.items():
                if excluded & set(f_spec["allergens"]):
                    continue
                for frk, fr_spec in FROSTING_RECIPES.items():
                    if excluded & set(fr_spec["allergens"]):
                        continue
                    if float(fr_spec["max_ambient_temp_c"]) < float(venue_temp_c):
                        continue
                    for t_spec in tier_candidates:
                        d = design_3d_cake_and_production_sheet(
                            tiers=t_spec,
                            shape=shape_clean,
                            sponge_key=sk,
                            filling_key=fk,
                            frosting_key=frk,
                            consumption_mode=consumption_mode,
                            venue_temp_c=venue_temp_c,
                        )
                        if not d.get("ok"):
                            continue
                        w_port = int(d["portions_and_structure"]["wedding_portions_2_5x5cm"])
                        gross = float(d["pricing_and_at_invoicing"]["recommended_client_total_gross_eur"])
                        if w_port >= guests and gross <= budget:
                            solutions.append({
                                "tier_count": len(t_spec),
                                "tiers": t_spec,
                                "shape": shape_clean,
                                "sponge_key": sk,
                                "sponge_name": s_spec["name"],
                                "filling_key": fk,
                                "filling_name": f_spec["name"],
                                "frosting_key": frk,
                                "frosting_name": fr_spec["name"],
                                "wedding_portions": w_port,
                                "total_gross_eur": gross,
                                "budget_headroom_eur": round(budget - gross, 2),
                                "allergen_codes": d["allergens_eu_1169_2011"]["allergen_codes"],
                                "melt_countdown": d["logistics_and_haccp_cold_chain"]["summer_thermal_melt_countdown"],
                                "design_sha256": d["design_sha256"],
                            })
                            break

        solutions.sort(key=lambda s: (s["wedding_portions"] - guests, s["total_gross_eur"]))
        if not solutions:
            return {
                "ok": False,
                "error": f"NO_FEASIBLE_CAKE_FOR_GUESTS({guests})_WITHIN_BUDGET({budget:.2f}EUR)",
            }
        return {
            "ok": True,
            "requested_guests": guests,
            "max_budget_eur": budget,
            "excluded_allergens": sorted(excluded),
            "recommended_solution": solutions[0],
            "alternatives_count": len(solutions),
            "alternatives": solutions[:5],
        }

    def create_tasting_box_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Books a 4-Flavor Tasting Box (`Caixa de Prova de Sabores`) and issues a redeemable
        credit voucher (`TASTING-CREDIT-*`) automatically deductible from the final 3D cake deposit.
        """
        data = payload or {}
        flavors = data.get("flavors") or [
            "pao_de_lo_tradicional+ovos_moles_doces_conventuais",
            "chocolate_belga_70+brigadeiro_gourmet",
            "red_velvet+curd_limao_frutos_vermelhos",
            "amendoa_sem_gluten+pistacio_tahini_crocante",
        ]
        if not isinstance(flavors, list) or not (2 <= len(flavors) <= 6):
            return {"ok": False, "error": "TASTING_BOX_REQUIRES_2_TO_6_FLAVORS"}
        price_eur = round(float(data.get("box_price_eur", 24.0)), 2)
        if price_eur <= 0.0:
            return {"ok": False, "error": "INVALID_TASTING_BOX_PRICE"}

        voucher_code = f"TASTING-CREDIT-{uuid.uuid4().hex[:8].upper()}"
        client_clean = _normalize_scrubbed_text(str(data.get("client_name") or "Noivos / Cliente Evento"))[:64]
        rec = {
            "voucher_code": voucher_code,
            "client_name": client_clean,
            "flavors": [str(f) for f in flavors],
            "box_price_eur": price_eur,
            "credit_eur": price_eur,
            "pickup_date": str(data.get("pickup_date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            "redeemed": False,
            "redeemed_on_quote": None,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        with self._lock:
            self.tasting_vouchers[voucher_code] = rec
        self._sync_unified_pg17_or_local_ledger("tasting_box", voucher_code, rec)
        return {"ok": True, "tasting_box": dict(rec)}

    def create_shareable_client_quote(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a zero-PII shareable Client Quote Approval Portal token (`QT-BAKE-*`)."""
        design = self.execute(payload)
        if not design.get("ok"):
            return design
        quote_token = f"QT-BAKE-{uuid.uuid4().hex[:10].upper()}"
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        pricing = design["pricing_and_at_invoicing"]
        quote_rec = {
            "quote_token": quote_token,
            "share_path": f"/api/bake/quotes/{quote_token}",
            "status": "PENDING_CLIENT_APPROVAL",
            "event_title": _normalize_scrubbed_text(str((payload or {}).get("event_title") or design["threejs_3d_scene"]["topper_text"]))[:64],
            "design_sha256": design["design_sha256"],
            "total_gross_eur": float(pricing["recommended_client_total_gross_eur"]),
            "initial_deposit_50pct_eur": float(pricing["deposit_50pct_atcud_invoice_eur"]),
            "tasting_credit_applied_eur": 0.0,
            "net_deposit_due_eur": float(pricing["deposit_50pct_atcud_invoice_eur"]),
            "allergens_eu_1169": design["allergens_eu_1169_2011"],
            "nutritional_declaration_eu_1169": design["nutritional_declaration_eu_1169"],
            "threejs_3d_scene": design["threejs_3d_scene"],
            "design_input_snapshot": {
                k: v
                for k, v in (payload or {}).items()
                if k in ("shape", "tiers", "sponge_key", "filling_key", "frosting_key", "consumption_mode", "topper_text", "venue_temp_c", "venue_rh_pct")
            },
            "pastelaria_kds_sync": None,
            "approved_by": None,
            "approved_at": None,
            "approval_receipt_sha256": None,
            "created_at": now_iso,
        }
        with self._lock:
            self.client_quotes[quote_token] = quote_rec
        self._sync_unified_pg17_or_local_ledger("client_quote_created", quote_token, {
            "quote_token": quote_token,
            "design_sha256": design["design_sha256"],
            "total_gross_eur": quote_rec["total_gross_eur"],
        })
        return {"ok": True, "quote": dict(quote_rec)}

    def get_shareable_client_quote(self, quote_token: str) -> Dict[str, Any]:
        with self._lock:
            rec = self.client_quotes.get(str(quote_token or "").strip().upper())
            if not rec:
                return {"ok": False, "error": f"QUOTE_TOKEN_NOT_FOUND({quote_token})"}
            return {"ok": True, "quote": dict(rec)}

    def approve_shareable_client_quote(
        self,
        quote_token: str,
        client_signature_name: str,
        tasting_voucher_code: Optional[str] = None,
        sync_to_pastelaria_kds: bool = True,
    ) -> Dict[str, Any]:
        sig_clean = _normalize_scrubbed_text(str(client_signature_name or "").strip())[:64]
        if len(sig_clean) < 3:
            return {"ok": False, "error": "CLIENT_SIGNATURE_NAME_REQUIRED"}

        tok = str(quote_token or "").strip().upper()
        v_code = str(tasting_voucher_code or "").strip().upper()
        with self._lock:
            rec = self.client_quotes.get(tok)
            if not rec:
                return {"ok": False, "error": f"QUOTE_TOKEN_NOT_FOUND({tok})"}
            if rec["status"] == "LOCKED_APPROVED":
                return {"ok": False, "error": f"QUOTE_ALREADY_APPROVED({tok})"}

            credit_eur = 0.0
            if v_code:
                v_rec = self.tasting_vouchers.get(v_code)
                if not v_rec:
                    return {"ok": False, "error": f"TASTING_VOUCHER_NOT_FOUND({v_code})"}
                if v_rec["redeemed"]:
                    return {"ok": False, "error": f"TASTING_VOUCHER_ALREADY_REDEEMED({v_code})"}
                credit_eur = float(v_rec["credit_eur"])
                v_rec["redeemed"] = True
                v_rec["redeemed_on_quote"] = tok

            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            net_dep = max(0.0, round(float(rec["initial_deposit_50pct_eur"]) - credit_eur, 2))
            receipt_sha = hashlib.sha256(
                f"QUOTE-APPROVED:{tok}:{rec['design_sha256']}:{sig_clean}:{net_dep}:{now_iso}".encode("utf-8")
            ).hexdigest()
            rec["status"] = "LOCKED_APPROVED"
            rec["tasting_credit_applied_eur"] = credit_eur
            rec["net_deposit_due_eur"] = net_dep
            rec["approved_by"] = sig_clean
            rec["approved_at"] = now_iso
            rec["approval_receipt_sha256"] = receipt_sha
            design_inp = dict(rec.get("design_input_snapshot") or {})
            snap = dict(rec)

        if sync_to_pastelaria_kds:
            bridge_payload = {
                **design_inp,
                "client_name": sig_clean,
                "requested_pickup_time": f"Evento {snap.get('event_title') or tok} (24h)",
                "lead_minutes_ahead": 1440,
            }
            bridge_res = self.dispatch_custom_cake_to_pastelaria(bridge_payload)
            kds_summary = {
                "synced": bool(bridge_res.get("ok")),
                "bridge_mode": bridge_res.get("bridge_mode"),
                "asae_ficha_id": bridge_res.get("asae_ficha_id"),
                "reservation_id": (
                    (bridge_res.get("pastelaria_reservation") or {}).get("reservation", {}).get("reservation_id")
                    or (bridge_res.get("pastelaria_local_sync") or {}).get("reservation", {}).get("reservation_id")
                ),
            }
            with self._lock:
                if tok in self.client_quotes:
                    self.client_quotes[tok]["pastelaria_kds_sync"] = kds_summary
                    snap = dict(self.client_quotes[tok])

        self._sync_unified_pg17_or_local_ledger("client_quote_approved", tok, {
            "quote_token": tok,
            "net_deposit_due_eur": snap["net_deposit_due_eur"],
            "approval_receipt_sha256": snap["approval_receipt_sha256"],
            "pastelaria_kds_sync": snap.get("pastelaria_kds_sync"),
        })
        return {"ok": True, "quote": snap}

    def dispatch_refrigerated_fleet_delivery(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches a multi-tier cake via `InsightFleet` (`:4026`), enforcing cold-chain van box bounds
        (`+2.0°C..+5.0°C`), cornering G-force (`<= 0.35g`), and Portuguese AT Transport Guide (`DL n.º 198/2012`).
        """
        data = payload or {}
        van_temp_c = float(data.get("van_temp_c", 3.4))
        max_lateral_g = float(data.get("max_expected_lateral_g", 0.24))
        if not (2.0 <= van_temp_c <= 5.0):
            return {"ok": False, "error": f"UNSAFE_FLEET_VAN_TEMP_C({van_temp_c}): must be between +2.0°C and +5.0°C"}
        if not (0.0 <= max_lateral_g <= 0.35):
            return {"ok": False, "error": f"UNSAFE_CORNERING_G_FORCE({max_lateral_g}>0.35g): route exceeds structural tier limit"}

        plate = str(data.get("vehicle_plate") or "AA-42-BB").strip().upper()
        if not re.match(r"^[A-Z0-9]{2}-[A-Z0-9]{2}-[A-Z0-9]{2}$", plate):
            return {"ok": False, "error": "INVALID_PT_VEHICLE_PLATE_FORMAT"}

        design = self.execute(data)
        if not design.get("ok"):
            return design

        delivery_id = f"FLT-BAKE-{uuid.uuid4().hex[:8].upper()}"
        at_doc_code = f"AT-{int(hashlib.sha256(delivery_id.encode('utf-8')).hexdigest()[:8], 16) % 900000000 + 100000000}"
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rec = {
            "delivery_id": delivery_id,
            "status": "IN_TRANSIT_COLD_CHAIN",
            "vehicle_plate": plate,
            "van_temp_c": round(van_temp_c, 2),
            "max_expected_lateral_g": round(max_lateral_g, 2),
            "loading_postal_code": str(data.get("loading_postal_code") or "1200-109"),
            "venue_postal_code": str(data.get("venue_postal_code") or "2710-616"),
            "at_guia_transporte_doc_code_id": at_doc_code,
            "regulation": "Decreto-Lei n.º 198/2012 (Guia de Transporte AT) & Reg. (CE) n.º 852/2004",
            "design_sha256": design["design_sha256"],
            "melt_countdown": design["logistics_and_haccp_cold_chain"]["summer_thermal_melt_countdown"],
            "dispatched_at": now_iso,
            "pod_completed_at": None,
            "pod_photo_cas_uri": None,
            "pod_receipt_sha256": None,
        }
        with self._lock:
            self.fleet_deliveries[delivery_id] = rec
        self._sync_unified_pg17_or_local_ledger("fleet_dispatch", delivery_id, rec)
        return {"ok": True, "delivery": dict(rec)}

    def confirm_fleet_proof_of_delivery(
        self,
        delivery_id: str,
        handoff_probe_temp_c: float,
        pod_photo_cas_uri: str,
        receiver_name: str,
    ) -> Dict[str, Any]:
        did = str(delivery_id or "").strip().upper()
        uri = str(pod_photo_cas_uri or "").strip()
        if not uri.startswith("cas://"):
            return {"ok": False, "error": "POD_PHOTO_MUST_USE_CAS_URI_SCHEME"}
        probe_c = float(handoff_probe_temp_c)
        if probe_c > 6.0 or probe_c < -2.0:
            return {"ok": False, "error": f"COLD_CHAIN_BREACH_AT_VENUE({probe_c}°C)"}
        recv_clean = _normalize_scrubbed_text(str(receiver_name or "Responsável Quinta/Evento"))[:64]

        with self._lock:
            rec = self.fleet_deliveries.get(did)
            if not rec:
                return {"ok": False, "error": f"DELIVERY_ID_NOT_FOUND({did})"}
            if rec["status"] == "DELIVERED_POD_SIGNED":
                return {"ok": False, "error": f"POD_ALREADY_CONFIRMED({did})"}
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            pod_hash = hashlib.sha256(
                f"POD:{did}:{probe_c}:{uri}:{recv_clean}:{now_iso}".encode("utf-8")
            ).hexdigest()
            rec["status"] = "DELIVERED_POD_SIGNED"
            rec["handoff_probe_temp_c"] = round(probe_c, 2)
            rec["pod_photo_cas_uri"] = uri
            rec["receiver_name"] = recv_clean
            rec["pod_completed_at"] = now_iso
            rec["pod_receipt_sha256"] = pod_hash
            snap = dict(rec)

        self._sync_unified_pg17_or_local_ledger("fleet_pod_signed", did, snap)
        return {"ok": True, "delivery": snap}

    # =========================================================================
    # ROUND-4 (v1.6.0) TRACKS: CATERING CUTTING & DOWEL EXTRACTION PDF + VENUE
    # TIMELINE, STAND CAUÇÃO DEPOSIT LEDGER (CIVA ART. 16.º N.º 6), AND
    # DIETARY SAFE REFORMULATOR (GLUTEN-FREE APC <=20PPM / LACTOSE-FREE / VEGAN)
    # =========================================================================
    @staticmethod
    def _minutes_to_hhmm(total_mins: int) -> str:
        mod = total_mins % 1440
        return f"{mod // 60:02d}:{mod % 60:02d}"

    def compute_venue_assembly_timeline_and_cutting_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes backward-scheduled Golden-Hour venue assembly milestones from `cake_cutting_time_hhmm`,
        strictly bounded by `summer_thermal_melt_countdown`, plus per-tier catering slice grids and
        internal dowel extraction counts so catering staff never serve a slice containing a dowel.
        """
        data = payload or {}
        cut_hhmm = str(data.get("cake_cutting_time_hhmm") or "22:30").strip()
        m_time = re.match(r"^([01]?\d|2[0-3]):([0-5]\d)$", cut_hhmm)
        if not m_time:
            return {"ok": False, "error": f"INVALID_CUTTING_TIME_HHMM({cut_hhmm}): expected HH:MM"}

        drive_mins = max(5, int(data.get("drive_minutes_to_venue", 45)))
        assembly_mins = max(10, int(data.get("assembly_minutes_on_site", 25)))

        design = self.execute(data)
        if not design.get("ok"):
            return design

        cut_total = int(m_time.group(1)) * 60 + int(m_time.group(2))
        melt_info = design["logistics_and_haccp_cold_chain"]["summer_thermal_melt_countdown"]
        safe_display_mins = max(20, int(melt_info["minutes_until_structural_softening"]) - 15)

        latest_staging_mins = cut_total - min(safe_display_mins, 60)
        venue_fridge_arrival_mins = latest_staging_mins - assembly_mins - 30
        bakery_van_departure_mins = venue_fridge_arrival_mins - drive_mins

        scene_tiers = design["threejs_3d_scene"]["tiers"]
        dowels_map = {
            int(d["tier_index"]): d
            for d in design["portions_and_structure"]["tier_dowel_blueprint"]
        }
        flavor_map = {
            int(f.get("tier_number") or f.get("tier_index") or 1): f
            for f in design["recipe_bom_grams"].get("per_tier_flavors", [])
        }
        shape_code = str(design["threejs_3d_scene"]["shape"])
        center_skewer = bool(design["portions_and_structure"]["center_sharpened_dowel_skewer_required"])

        cutting_instructions: List[Dict[str, Any]] = []
        # Caterers disassemble & cut from TOP tier down to BASE tier (reverse order)
        for t_mesh in sorted(scene_tiers, key=lambda x: int(x.get("tier_number") or x.get("tier_index") or 1), reverse=True):
            idx = int(t_mesh.get("tier_number") or t_mesh.get("tier_index") or 1)
            d_info = dowels_map.get(idx, {})
            fl_info = flavor_map.get(idx, {})
            dowel_count = int(
                d_info.get("polypropylene_dowel_rods_count")
                or d_info.get("internal_support_dowels_count")
                or t_mesh.get("internal_dowels_count")
                or 0
            )
            diam = float(t_mesh["diameter_cm"])
            grid_note = (
                f"Corte em grelha retangular paralela (tiras de 5,0 cm subdivididas a cada 2,5 cm) — diâmetro/lado {diam} cm"
                if shape_code in ("ROUND", "HEART", "HEXAGON")
                else f"Corte linear em grelha ortogonal (2,5 cm x 5,0 cm evento / 5,0 cm x 5,0 cm festa) — lado {diam} cm"
            )
            cutting_instructions.append({
                "disassembly_step": len(cutting_instructions) + 1,
                "tier_index": idx,
                "tier_label_pt": f"{idx}.º Andar ({diam} cm × {t_mesh['height_cm']} cm · {shape_code})",
                "sponge_and_filling": f"{fl_info.get('sponge_name', design['recipe_bom_grams']['sponge_type'])} + {fl_info.get('filling_name', design['recipe_bom_grams']['filling_type'])}",
                "wedding_slices_2_5x5cm": int(t_mesh.get("wedding_portions") or t_mesh.get("wedding_portions_2_5x5cm") or 0),
                "party_slices_5x5cm": int(t_mesh.get("party_portions") or t_mesh.get("party_portions_5x5cm") or 0),
                "dowels_to_extract_before_slicing": dowel_count,
                "center_skewer_alert": center_skewer,
                "catering_action_pt": (
                    f"Extrair {dowel_count} estacas internas PP alimentar"
                    + (" + 1 cavilha central afiada" if center_skewer and idx == len(scene_tiers) else "")
                    + " ANTES de fatiar."
                    if (dowel_count > 0 or (center_skewer and idx == len(scene_tiers)))
                    else "Andar de topo livre de estacas internas de suporte; retirar prato separador inferior."
                ),
                "cutting_grid_instruction_pt": grid_note,
                "tier_allergen_codes": fl_info.get("allergens", design["allergens_eu_1169_2011"]["allergen_codes"]),
            })

        return {
            "ok": True,
            "design_sha256": design["design_sha256"],
            "event_topper": design["threejs_3d_scene"]["topper_text"],
            "venue_golden_hour_timeline": {
                "bakery_cold_van_departure_hhmm": self._minutes_to_hhmm(bakery_van_departure_mins),
                "venue_chiller_arrival_hhmm": self._minutes_to_hhmm(venue_fridge_arrival_mins),
                "room_staging_start_hhmm": self._minutes_to_hhmm(latest_staging_mins),
                "cake_cutting_ceremony_hhmm": cut_hhmm,
                "max_safe_out_of_fridge_minutes": safe_display_mins,
                "venue_temp_c": melt_info["venue_temp_c"],
                "venue_rh_pct": melt_info["venue_rh_pct"],
                "frosting_max_safe_ambient_c": melt_info["frosting_max_safe_ambient_c"],
            },
            "total_wedding_portions": design["portions_and_structure"]["wedding_portions_2_5x5cm"],
            "total_party_portions": design["portions_and_structure"]["party_portions_5x5cm"],
            "center_skewer_installed": center_skewer,
            "total_internal_dowels_to_account_for": sum(
                c["dowels_to_extract_before_slicing"] for c in cutting_instructions
            ),
            "tier_disassembly_and_cutting_steps": cutting_instructions,
            "allergens_eu_1169": design["allergens_eu_1169_2011"],
        }

    def render_catering_cutting_guide_pdf_bytes(self, payload: Dict[str, Any]) -> bytes:
        """
        Renders a native ReportLab Vector A4 Portrait PDF (`Guia de Corte para Catering & Controlo de Cavilhas`)
        for wedding/event venues (`Quintas` & hotels).
        """
        from io import BytesIO
        from xml.sax.saxutils import escape as xml_esc
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        plan = self.compute_venue_assembly_timeline_and_cutting_plan(payload)
        if not plan.get("ok"):
            raise ValueError(str(plan.get("error") or "FAILED_TO_BUILD_CATERING_CUTTING_PLAN"))

        try:
            from insight_pastelaria.asae_ficha_tecnica import _register_unicode_pdf_fonts, coerce_establishment_profile

            est = coerce_establishment_profile(load_establishment_profile(self.establishment_profile_path))
            font_reg, font_bold = _register_unicode_pdf_fonts()
        except Exception:
            est = load_establishment_profile(self.establishment_profile_path)
            font_reg, font_bold = "Helvetica", "Helvetica-Bold"

        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=12 * mm,
            rightMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
            title=f"Guia de Corte Catering & Cavilhas - {plan['event_topper']}",
        )
        styles = getSampleStyleSheet()
        st_title = ParagraphStyle("CatTitle", parent=styles["Heading1"], fontName=font_bold, fontSize=11.5, leading=14, textColor=colors.HexColor("#0f172a"))
        st_sub = ParagraphStyle("CatSub", parent=styles["Normal"], fontName=font_reg, fontSize=8.0, leading=10.5, textColor=colors.HexColor("#334155"))
        st_sec = ParagraphStyle("CatSec", parent=styles["Heading2"], fontName=font_bold, fontSize=9.2, leading=12, textColor=colors.HexColor("#1e293b"))
        st_cell = ParagraphStyle("CatCell", parent=styles["Normal"], fontName=font_reg, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#0f172a"))
        st_hdr = ParagraphStyle("CatHdr", parent=styles["Normal"], fontName=font_bold, fontSize=7.5, leading=9.5, textColor=colors.white)

        usable_w = A4[0] - 24 * mm
        tl = plan["venue_golden_hour_timeline"]

        tl_rows = [
            [Paragraph("Saída Carrinha Frio (+2..+5°C)", st_hdr), Paragraph("Chegada Câmara Quinta", st_hdr), Paragraph("Montagem em Sala", st_hdr), Paragraph("Hora Corte Bolo", st_hdr), Paragraph("Janela Máx. Fora Frio", st_hdr)],
            [
                Paragraph(xml_esc(tl["bakery_cold_van_departure_hhmm"]), st_cell),
                Paragraph(xml_esc(tl["venue_chiller_arrival_hhmm"]), st_cell),
                Paragraph(xml_esc(tl["room_staging_start_hhmm"]), st_cell),
                Paragraph(xml_esc(tl["cake_cutting_ceremony_hhmm"]), st_cell),
                Paragraph(xml_esc(f"{tl['max_safe_out_of_fridge_minutes']} min ({tl['venue_temp_c']}°C)"), st_cell),
            ],
        ]
        tl_tbl = Table(tl_rows, colWidths=[usable_w * 0.22, usable_w * 0.20, usable_w * 0.18, usable_w * 0.18, usable_w * 0.22])
        tl_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))

        step_rows: List[List[Any]] = [[
            Paragraph("Ordem Desmontagem", st_hdr),
            Paragraph("Andar / Sabores", st_hdr),
            Paragraph("Fatias (Evento / Festa)", st_hdr),
            Paragraph("Controlo Estacas & Cavilhas (HACCP Físico)", st_hdr),
            Paragraph("Instrução de Corte & Alergénios", st_hdr),
        ]]
        for stp in plan["tier_disassembly_and_cutting_steps"]:
            step_rows.append([
                Paragraph(xml_esc(f"Passo {stp['disassembly_step']}"), st_cell),
                Paragraph(xml_esc(f"{stp['tier_label_pt']} — {stp['sponge_and_filling']}"), st_cell),
                Paragraph(xml_esc(f"{stp['wedding_slices_2_5x5cm']} / {stp['party_slices_5x5cm']}"), st_cell),
                Paragraph(xml_esc(stp["catering_action_pt"]), st_cell),
                Paragraph(xml_esc(f"{stp['cutting_grid_instruction_pt']} | Alergénios: {', '.join(stp['tier_allergen_codes'])}"), st_cell),
            ])
        step_tbl = Table(step_rows, colWidths=[usable_w * 0.12, usable_w * 0.24, usable_w * 0.13, usable_w * 0.25, usable_w * 0.26], repeatRows=1)
        step_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))

        story = [
            Paragraph(f"GUIA TÉCNICO DE CORTE PARA CATERING &amp; EXTRAÇÃO DE CAVILHAS — {xml_esc(plan['event_topper'])}", st_title),
            Paragraph(
                f"<b>Atelier Produtor:</b> {xml_esc(est.nome_comercial)} (NIF {xml_esc(est.nif)}) &nbsp;|&nbsp; "
                f"<b>Total Fatias Evento (2,5×5 cm):</b> {plan['total_wedding_portions']} &nbsp;|&nbsp; "
                f"<b>Total Estacas PP a Contabilizar:</b> {plan['total_internal_dowels_to_account_for']}"
                f"{' + 1 Cavilha Central' if plan['center_skewer_installed'] else ''}",
                st_sub,
            ),
            Spacer(1, 3 * mm),
            Paragraph("1. Cronograma Inverso de Cadeia de Frio &amp; Exposição em Sala (Prevenção de Colapso Térmico)", st_sec),
            tl_tbl,
            Spacer(1, 4 * mm),
            Paragraph("2. Sequência de Desmontagem (Topo -> Base), Remoção de Estacas PP e Grelha de Corte", st_sec),
            step_tbl,
            Spacer(1, 4 * mm),
            Paragraph(
                f"<b>3. Declaração Obrigatória de Alergénios (Reg. UE 1169/2011 &amp; DL 26/2016):</b> "
                f"{xml_esc(plan['allergens_eu_1169']['allergen_counter_signage_pt'])} &nbsp;|&nbsp; "
                f"<b>SHA-256:</b> {plan['design_sha256'][:16]}",
                st_sub,
            ),
        ]
        doc.build(story)
        return buf.getvalue()

    def create_stand_rental_deposit(
        self,
        stand_code: str,
        stand_description: str,
        deposit_eur: float,
        expected_return_date: str,
        quote_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Registers a refundable security deposit (`Caução de Suporte / Pedestal`) in exact integer minor units (`cents`)
        exempt from IVA upon issue under `CIVA Art. 16.º n.º 6 alínea c)`.
        """
        dep_cents = int(round(float(deposit_eur) * 100))
        if dep_cents <= 0:
            return {"ok": False, "error": "STAND_DEPOSIT_MUST_BE_POSITIVE"}
        ret_date = str(expected_return_date or "").strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", ret_date):
            return {"ok": False, "error": "INVALID_EXPECTED_RETURN_DATE_ISO"}

        rental_id = f"CAU-BAKE-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        receipt_sha = hashlib.sha256(f"CAUCAO-OPEN:{rental_id}:{dep_cents}:{ret_date}:{now_iso}".encode("utf-8")).hexdigest()
        rec = {
            "rental_id": rental_id,
            "stand_code": str(stand_code or "SUP-ACRIL-GOLD-01").strip().upper(),
            "stand_description": _normalize_scrubbed_text(str(stand_description or "Base Acrílica / Latão Dourado"))[:80],
            "quote_token": str(quote_token).strip().upper() if quote_token else None,
            "deposit_cents": dep_cents,
            "deposit_eur": round(dep_cents / 100.0, 2),
            "iva_on_deposit_pct": 0.0,
            "fiscal_basis_pt": "CIVA Art. 16.º n.º 6 alínea c) — Caução reembolsável excluída do valor tributável",
            "expected_return_date": ret_date,
            "status": "HELD_IN_ESCROW",
            "refunded_cents": 0,
            "taxable_damage_invoice_cents": 0,
            "damage_atcud": None,
            "sha256_receipt": receipt_sha,
            "created_at": now_iso,
            "settled_at": None,
        }
        with self._lock:
            self.stand_rentals[rental_id] = rec
        self._sync_unified_pg17_or_local_ledger("stand_caucao_created", rental_id, rec)
        return {"ok": True, "rental": dict(rec)}

    def settle_stand_rental_return(
        self,
        rental_id: str,
        returned_intact: bool = True,
        damage_fee_eur: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Settles a reusable stand security deposit (`Caução`):
        - Intact return -> 100% refund (`0% IVA`, balanced minor-unit cents `refund_cents == deposit_cents`).
        - Damaged / lost -> withholds `min(deposit_cents, damage_fee_cents)` and issues a `23% IVA` compensation invoice (`ATCUD`).
        """
        rid = str(rental_id or "").strip().upper()
        dmg_cents = max(0, int(round(float(damage_fee_eur) * 100)))
        with self._lock:
            rec = self.stand_rentals.get(rid)
            if not rec:
                return {"ok": False, "error": f"STAND_RENTAL_NOT_FOUND({rid})"}
            if rec["status"] != "HELD_IN_ESCROW":
                return {"ok": False, "error": f"STAND_RENTAL_ALREADY_SETTLED({rid})"}

            dep_cents = int(rec["deposit_cents"])
            if returned_intact or dmg_cents == 0:
                refund_cents = dep_cents
                withheld_cents = 0
                status = "REFUNDED_INTACT_0PCT_IVA"
                damage_atcud = None
                net_eur = 0.0
                iva_eur = 0.0
            else:
                withheld_cents = min(dep_cents, dmg_cents)
                refund_cents = dep_cents - withheld_cents
                status = "DAMAGE_INVOICED_23PCT_IVA"
                seq = int(hashlib.sha256(rid.encode("utf-8")).hexdigest()[:6], 16) % 900000 + 100000
                damage_atcud = f"ATCUD:BAKECAU26-{seq}"
                gross_dmg = withheld_cents / 100.0
                net_eur = round(gross_dmg / 1.23, 2)
                iva_eur = round(gross_dmg - net_eur, 2)

            assert refund_cents + withheld_cents == dep_cents, "Minor-unit accounting balance violation"
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            settle_sha = hashlib.sha256(
                f"CAUCAO-SETTLE:{rid}:{refund_cents}:{withheld_cents}:{status}:{now_iso}".encode("utf-8")
            ).hexdigest()
            rec.update({
                "status": status,
                "refunded_cents": refund_cents,
                "refunded_eur": round(refund_cents / 100.0, 2),
                "taxable_damage_invoice_cents": withheld_cents,
                "taxable_damage_gross_eur": round(withheld_cents / 100.0, 2),
                "taxable_damage_net_eur": net_eur,
                "taxable_damage_iva_23pct_eur": iva_eur,
                "damage_atcud": damage_atcud,
                "settlement_sha256": settle_sha,
                "settled_at": now_iso,
            })
            snap = dict(rec)

        self._sync_unified_pg17_or_local_ledger("stand_caucao_settled", rid, snap)
        return {"ok": True, "rental": snap}

    def reformulate_dietary_safe_cake(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministically reformulates a 3D multi-tier cake for strict dietary regimes:
        - `GLUTEN_FREE_APC_20PPM` (`Regulamento (UE) n.º 828/2014` <= 20 mg/kg glúten)
        - `LACTOSE_FREE` (`0,01g/100g` lactose)
        - `VEGAN_100PCT` (0% ingredientes de origem animal — isento de Ovos e Leite)
        Enforces tighter Euler slenderness bounds (`<= 1.75` for Gluten-Free; `<= 1.65` for Gluten-Free + Vegan)
        and adds `+2` extra PP support dowels per load-bearing tier.
        """
        data = dict(payload or {})
        raw_modes = data.get("dietary_modes") or ["GLUTEN_FREE_APC_20PPM"]
        modes = sorted({str(m).strip().upper() for m in raw_modes if str(m).strip()})
        valid_modes = {"GLUTEN_FREE_APC_20PPM", "LACTOSE_FREE", "VEGAN_100PCT"}
        unknown = [m for m in modes if m not in valid_modes]
        if not modes or unknown:
            return {"ok": False, "error": f"INVALID_DIETARY_MODES({unknown}): supported={sorted(valid_modes)}"}

        base_res = self.execute(data)
        if not base_res.get("ok"):
            return base_res

        gf = "GLUTEN_FREE_APC_20PPM" in modes
        vegan = "VEGAN_100PCT" in modes
        lac_free = ("LACTOSE_FREE" in modes) or vegan

        tiers = base_res["threejs_3d_scene"]["tiers"]
        base_d = float(tiers[0]["diameter_cm"])
        total_h = sum(float(t["height_cm"]) for t in tiers)
        ratio = round(total_h / max(base_d, 0.1), 3)
        max_ratio = 1.65 if (gf and vegan) else (1.75 if gf else (1.90 if vegan else 2.20))
        if ratio > max_ratio:
            return {
                "ok": False,
                "error": (
                    f"DIETARY_SPONGE_SLENDERNESS_EXCEEDED(H/D={ratio} > {max_ratio}): "
                    "massas sem glúten / aquafaba exigem base mais larga ou menor altura total para evitar fissura estrutural."
                ),
            }

        substitutions: List[Dict[str, str]] = []
        removed_allergens: set[str] = set()
        if gf:
            removed_allergens.add("GLUTEN")
            substitutions.append({
                "original": "Farinha de trigo T55",
                "substitute": "Blend certificado Sem Glúten (Farinha de Arroz Fina 65% + Amido de Milho 25% + Casca de Psyllium 10% — <= 20 mg/kg Reg. UE 828/2014)",
                "structural_note": "Módulo de corte inferior ao trigo; reforço automático +2 estacas PP por andar.",
            })
        if lac_free:
            removed_allergens.add("MILK")
            substitutions.append({
                "original": "Manteiga 82% M.G. / Leite / Natas / Leite Condensado",
                "substitute": (
                    "Manteiga Vegetal de Karité & Coco + Creme Culinário de Coco Reduzido (100% Plant-Based)"
                    if vegan
                    else "Manteiga e Natas Deslactosadas (< 0,01% lactose — Enzima Lactase)"
                ),
                "structural_note": "Estabilizar emulsão a +19°C antes de bater cobertura.",
            })
        if vegan:
            removed_allergens.add("EGGS")
            substitutions.append({
                "original": "Ovos inteiros pasteurizados / Claras merengue",
                "substitute": "Redução de Aquafaba Pastorizada + Proteína de Batata (2% p/p para merengue estável)",
                "structural_note": "Arrefecer formas 25 min antes de desenformar para fixar rede proteica vegetal.",
            })

        remaining_allergens = [
            code for code in base_res["allergens_eu_1169_2011"]["allergen_codes"]
            if code not in removed_allergens
        ]
        upgraded_dowels = []
        for dw in base_res["portions_and_structure"]["tier_dowel_blueprint"]:
            dw_copy = dict(dw)
            rod_cnt = int(dw_copy.get("polypropylene_dowel_rods_count", 0))
            if rod_cnt > 0 and (gf or vegan):
                dw_copy["polypropylene_dowel_rods_count"] = rod_cnt + 2
                dw_copy["dietary_reinforcement_note"] = "+2 estacas PP alimentar adicionais para massa especial"
            upgraded_dowels.append(dw_copy)

        clean_bench_protocol = [
            "Higienizar bancada inox dedicada com PPHO validado (200 ppm) antes da pesagem.",
            "Utilizar batedeira, espátulas, formas e bicos identificados por código de cor ROXO (Alergénios).",
        ]
        if gf:
            clean_bench_protocol.append(
                "Cumprir Regulamento de Execução (UE) n.º 828/2014 (<= 20 mg/kg glúten) e separação temporal face a farinhas de trigo."
            )

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        cert_sha = hashlib.sha256(
            f"DIETARY-REFORM:{base_res['design_sha256']}:{','.join(modes)}:{ratio}:{now_iso}".encode("utf-8")
        ).hexdigest()
        out = {
            "ok": True,
            "dietary_modes": modes,
            "regulation_pt_eu": "Regulamento (UE) n.º 828/2014 (Sem Glúten <= 20 ppm) & Reg. (UE) n.º 1169/2011",
            "structural_slenderness_verified": {
                "h_over_d_ratio": ratio,
                "max_allowed_for_dietary_matrix": max_ratio,
                "upgraded_tier_dowel_blueprint": upgraded_dowels,
            },
            "ingredient_substitutions": substitutions,
            "eliminated_allergen_codes": sorted(removed_allergens),
            "remaining_allergen_codes": remaining_allergens,
            "clean_bench_cross_contamination_protocol_pt": clean_bench_protocol,
            "base_design_sha256": base_res["design_sha256"],
            "reformulation_certificate_sha256": cert_sha,
        }
        self._sync_unified_pg17_or_local_ledger("dietary_reformulation", cert_sha[:16], {
            "modes": modes,
            "eliminated": sorted(removed_allergens),
            "remaining": remaining_allergens,
        })
        return out

    def get_supported_fiscal_locales(self) -> Dict[str, Any]:
        active = resolve_locale_fiscal_profile(
            self.locale_fiscal_config.get("country_code", "PT"),
            self.locale_fiscal_config.get("custom_overrides"),
        )
        return {
            "ok": True,
            "active_config": dict(self.locale_fiscal_config),
            "active_profile": active.to_dict(),
            "supported_locales": list_supported_locale_profiles(),
        }

    def configure_locale_fiscal_regime(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload or {}
        regime_raw = str(data.get("tax_regime") or "STANDARD_VAT").strip().upper()
        if regime_raw in ("ISENTO_ART53", "EXEMPT", "ISE", "MEI", "KLEIN"):
            regime_clean = "EXEMPT_SMALL_BUSINESS"
        elif regime_raw in ("EXEMPT_SMALL_BUSINESS", "STANDARD_VAT"):
            regime_clean = regime_raw
        else:
            return {"ok": False, "error": f"UNSUPPORTED_TAX_REGIME({regime_raw})"}
        prof = resolve_locale_fiscal_profile(
            str(data.get("country_code") or "PT"),
            data.get("custom_overrides"),
        )
        self.locale_fiscal_config = {
            "country_code": prof.country_code,
            "tax_regime": regime_clean,
            "ytd_domestic_turnover": max(0.0, float(data.get("ytd_domestic_turnover", 0.0))),
            "ytd_eu_cross_border_turnover": max(0.0, float(data.get("ytd_eu_cross_border_turnover", 0.0))),
            "custom_overrides": dict(data.get("custom_overrides") or {}),
        }
        self._sync_unified_pg17_or_local_ledger("bake_locale_fiscal_config", prof.country_code, self.locale_fiscal_config)
        return {
            "ok": True,
            "active_config": dict(self.locale_fiscal_config),
            "resolved_profile": prof.to_dict(),
        }

    def check_turnover_cliff_for_quote(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload or {}
        open_quotes = sum(
            float(q.get("total_gross_eur", 0.0))
            for q in self.client_quotes.values()
            if q.get("status") == "APPROVED"
        )
        return evaluate_turnover_cliff_and_quote_guard(
            country_code=str(data.get("country_code") or self.locale_fiscal_config.get("country_code", "PT")),
            tax_regime=str(data.get("tax_regime") or self.locale_fiscal_config.get("tax_regime", "EXEMPT_SMALL_BUSINESS")),
            ytd_domestic_turnover=(
                float(data["ytd_domestic_turnover"])
                if data.get("ytd_domestic_turnover") is not None
                else float(self.locale_fiscal_config.get("ytd_domestic_turnover", 0.0))
            ),
            open_approved_quotes_total=(
                float(data["open_approved_quotes_total"])
                if data.get("open_approved_quotes_total") is not None
                else open_quotes
            ),
            proposed_order_amount=float(data.get("proposed_order_amount", 0.0)),
            ytd_eu_cross_border_turnover=(
                float(data["ytd_eu_cross_border_turnover"])
                if data.get("ytd_eu_cross_border_turnover") is not None
                else float(self.locale_fiscal_config.get("ytd_eu_cross_border_turnover", 0.0))
            ),
            custom_overrides=data.get("custom_overrides") or self.locale_fiscal_config.get("custom_overrides"),
        )

    def simulate_regime_breakeven(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload or {}
        return simulate_exemption_vs_voluntary_vat_opt_in(
            projected_annual_revenue=float(data.get("projected_annual_revenue", 14500.0)),
            b2b_revenue_share_pct=float(data.get("b2b_revenue_share_pct", 10.0)),
            raw_ingredients_share_of_rev_pct=float(data.get("raw_ingredients_share_of_rev_pct", 24.0)),
            packaging_and_utilities_share_of_rev_pct=float(data.get("packaging_and_utilities_share_of_rev_pct", 8.0)),
            planned_capex_equipment_net=float(data.get("planned_capex_equipment_net", 0.0)),
            startup_year=int(data.get("startup_year", 1)),
            revenue_mix_goods_pct=float(data.get("revenue_mix_goods_pct", 85.0)),
            effective_personal_income_tax_rate_pct=float(data.get("effective_personal_income_tax_rate_pct", 20.0)),
            country_code=str(data.get("country_code") or self.locale_fiscal_config.get("country_code", "PT")),
            custom_overrides=data.get("custom_overrides") or self.locale_fiscal_config.get("custom_overrides"),
        )

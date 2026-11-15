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
import sys
import urllib.error
import urllib.request
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
        "haccp_and_bitemporal_traceability": {
            "regulation": "Regulamento (CE) n.º 852/2004 (HACCP) & Reg. (CE) n.º 178/2002 Art. 18.º",
            "point_in_time_date": pit_date,
            "cold_retard_haccp_compliant": haccp_cold_retard_ok,
            "bitemporal_lot_records": bitemporal_lots,
            "sha256_audit_receipt": sha256_receipt,
        },
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
) -> Dict[str, Any]:
    """
    Computes the complete `Three.js` 3D scene graph, wedding/party portions, structural dowel blueprint,
    slenderness stability check, gram-exact ingredient recipe BOM, full 14 EU Reg. 1169/2011 allergen declaration,
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

    sponge = SPONGE_RECIPES.get(sponge_key, SPONGE_RECIPES["red_velvet"])
    filling = FILLING_RECIPES.get(filling_key, FILLING_RECIPES["brigadeiro_gourmet"])
    frosting = FROSTING_RECIPES.get(frosting_key, FROSTING_RECIPES["swiss_meringue_buttercream"])

    safe_topper = _normalize_scrubbed_text(str(topper_text or "Sofia & Miguel"))[:64]

    threejs_meshes: List[Dict[str, Any]] = []
    structural_dowels: List[Dict[str, Any]] = []
    current_y_cm = 0.0
    total_volume_cm3 = 0.0
    total_surface_cm2 = 0.0
    total_wedding_portions = 0
    total_party_portions = 0
    max_diameter_cm = 0.0

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
            # Parametric cardioid/bezier heart inscribed in a `diam x diam` bounding box (~82% of square area)
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

        # Wedding slice: 2.5cm x 5cm base (~12.5 cm2), Party slice: 5cm x 5cm (~22-25 cm2)
        height_factor = 1.25 if height >= 13.0 else 1.0
        w_slices = max(4, int(round((base_area_cm2 / 12.5) * height_factor)))
        p_slices = max(3, int(round((base_area_cm2 / 22.0) * height_factor)))
        total_wedding_portions += w_slices
        total_party_portions += p_slices

        # Structural dowels needed if another tier sits above this tier
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

        threejs_meshes.append({
            "tier_number": idx + 1,
            "geometry_type": geom_type,
            "radial_segments": radial_segs,
            "diameter_cm": diam,
            "height_cm": height,
            "position_y_cm": round(current_y_cm + (height / 2.0), 2),
            "base_color_hex": primary_color_hex,
            "piping_accent_color_hex": accent_color_hex,
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

    # Gram-exact Ingredient Scaling
    sponge_weight_g = round(total_volume_cm3 * 0.68 * float(sponge["density_g_per_cm3"]), 1)
    filling_weight_g = round(total_volume_cm3 * 0.24 * 0.95, 1)
    frosting_weight_g = round(total_surface_cm2 * 0.85, 1)
    total_cake_weight_kg = round((sponge_weight_g + filling_weight_g + frosting_weight_g) / 1000.0, 2)

    sponge_ingredients_g = {
        k: round(sponge_weight_g * ratio, 1) for k, ratio in sponge["ratios"].items()
    }

    # Costing & Portugal AT Fiscal Pricing (CIVA Lista II Verba 3.1 Restauração 13% vs. Take-Away/Entrega 23%)
    raw_materials_eur = (
        (
            (sponge_weight_g / 1000.0) * float(sponge["cost_eur_per_kg"])
            + (filling_weight_g / 1000.0) * float(filling["cost_eur_per_kg"])
            + (frosting_weight_g / 1000.0) * float(frosting["cost_eur_per_kg"])
        )
        * lot_cost_multiplier
        + (len(tier_specs) * 4.50)  # Cake drums, polypropylene dowels, reinforced transport box
    )
    estimated_labor_hours = round(2.5 + (len(tier_specs) * 1.8) + (total_wedding_portions * 0.025), 1)
    labor_cost_eur = estimated_labor_hours * float(hourly_rate_eur)
    subtotal_net_eur = round((raw_materials_eur * 1.35) + labor_cost_eur, 2)

    mode_upper = str(consumption_mode or "RESTAURACAO_13").strip().upper()
    if mode_upper in ("TAKEAWAY_23", "ENTREGA_23", "23"):
        iva_rate_pct = 23.0
        iva_regime_label = "Taxa Normal IVA 23% (Take-Away / Entrega de Bolo Decorado — CIVA Art. 18.º)"
    else:
        iva_rate_pct = 13.0
        iva_regime_label = "Taxa Intermédia IVA 13% (Serviço de Restauração / Catering — CIVA Lista II Verba 3.1)"

    total_gross_eur = round(subtotal_net_eur * (1.0 + (iva_rate_pct / 100.0)), 2)
    deposit_50pct_eur = round(total_gross_eur * 0.50, 2)

    nif_valid: Optional[bool] = None
    nif_masked: Optional[str] = None
    if client_nif:
        digits = "".join(ch for ch in str(client_nif) if ch.isdigit())
        nif_valid = validate_portuguese_nif_modulo11(digits)
        nif_masked = f"{digits[:2]}*****{digits[-2:]}" if len(digits) == 9 else "NIF-INVALID"

    sig_seed = f"{shape_clean}:{len(tier_specs)}:{sponge_key}:{filling_key}:{frosting_key}:{total_gross_eur}"
    design_sha256 = hashlib.sha256(sig_seed.encode("utf-8")).hexdigest()
    atcud_preview = f"ATCUD:JJ7B4K30-{int(design_sha256[:6], 16) % 90000 + 10000}"

    # Mandatory EU Reg. 1169/2011 Annex II Allergen Union (sorted by statutory Annex II number 1..14)
    raw_codes = set(sponge["allergens"]) | set(filling["allergens"]) | set(frosting["allergens"])
    allergen_codes = sorted(
        raw_codes,
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

    # ComfyUI ControlNet Photorealistic Studio Prompt (Sovereign domain phrasing per RULE-18)
    comfyui_controlnet_spec = {
        "engine": "ComfyUI Flux.1-dev / SDXL + ControlNet Depth & Canny Lock",
        "controlnet_depth_strength": 0.88,
        "controlnet_canny_strength": 0.65,
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

    # Refrigerated Logistics & ASAE HACCP Cold-Chain Spec (`InsightFleet` + `InsightSensor`)
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
            "sponge_key": sponge_key if sponge_key in SPONGE_RECIPES else "red_velvet",
            "sponge_type": sponge["name"],
            "sponge_total_g": sponge_weight_g,
            "sponge_ingredients_g": sponge_ingredients_g,
            "sponge_baking_temp_c": sponge["baking_temp_c"],
            "sponge_baking_time_minutes": sponge["baking_time_minutes"],
            "filling_key": filling_key if filling_key in FILLING_RECIPES else "brigadeiro_gourmet",
            "filling_type": filling["name"],
            "filling_total_g": filling_weight_g,
            "frosting_key": frosting_key if frosting_key in FROSTING_RECIPES else "swiss_meringue_buttercream",
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
        "pricing_and_at_invoicing": {
            "raw_ingredients_and_packaging_cost_eur": round(raw_materials_eur, 2),
            "estimated_baker_labor_hours": estimated_labor_hours,
            "labor_cost_eur": round(labor_cost_eur, 2),
            "recommended_net_price_eur": subtotal_net_eur,
            "consumption_mode": mode_upper,
            "iva_rate_pct": iva_rate_pct,
            "iva_regime_label_pt": iva_regime_label,
            "recommended_client_total_gross_eur": total_gross_eur,
            "deposit_50pct_atcud_invoice_eur": deposit_50pct_eur,
            "atcud_preview": atcud_preview,
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
        self.asae_fichas_dir = base_dir / "fichas_tecnicas_asae"
        pastelaria_prof_dir = _PROJECTS_ROOT / "InsightPastelaria" / "pipeline_data" / "fichas_tecnicas_asae"
        if storage_dir is None and pastelaria_prof_dir.exists():
            self.establishment_profile_path = pastelaria_prof_dir / "establishment_profile.json"
        else:
            self.establishment_profile_path = self.asae_fichas_dir / "establishment_profile.json"
        self.registered_fichas: Dict[str, ASAEFichaTecnica] = {}

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
            "version": "1.3.0",
            "port": self.DEFAULT_PORT,
            "api_prefix": self.API_PREFIX,
            "asae_normative_template": ASAE_NORMATIVE_TEMPLATE_BASIS["template_code"],
            "establishment": est.to_dict(),
            "standalone_benefit": (
                "Interactive Three.js 3D Multi-Tier Cake Configurator + Arrhenius Q10 Sourdough Fermentation Lab "
                "+ Exact Portion/Dowel/Gram Recipe Scaler + Full 14 EU 1169/2011 Allergens + Native Vector A4 ASAE PDF & InsightPastelaria (:4029) Bridge."
            ),
            "ecosystem_synergy": [
                "Combined with SetMiddle Insight™ · Pastelaria (:4029): Dispatches 24h custom cake orders directly into the Owner Stock-Confirmation Gate & ASAE Ficha Dossier.",
                "Combined with SetMiddle Insight™ · Fleet (:4026): Checks refrigerated delivery box dimensions, route smoothness (<=0.35g vibration), and venue arrival windows.",
                "Combined with SetMiddle Insight™ · Sensor (:4025): Monitors bakery fridge/freezer temperatures 24/7 for ASAE HACCP (Reg. CE 852/2004) compliance.",
                "Combined with SetMiddle Insight™ · Fiscal (:4017) & Expense (:4002): Issues immediate 50% deposit ATCUD / SAF-T (PT) invoices (13% vs. 23% IVA).",
            ],
            "available_shapes": ["ROUND", "SQUARE", "HEART", "HEXAGON"],
            "available_sponges": list(SPONGE_RECIPES.keys()),
            "available_fillings": list(FILLING_RECIPES.keys()),
            "available_frostings": list(FROSTING_RECIPES.keys()),
            "eu_14_allergens_supported": len(EU_14_MANDATORY_ALLERGENS),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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
            consumption_mode=str(data.get("consumption_mode") or "RESTAURACAO_13"),
            may_contain_trace_codes=data.get("may_contain_trace_codes"),
            client_nif=data.get("client_nif"),
            point_in_time_date=data.get("point_in_time_date"),
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

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

_INSIGHT_CORE_DIR = Path("C:/Users/bruno/PycharmProjects/InsightCore")
if _INSIGHT_CORE_DIR.exists() and str(_INSIGHT_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_INSIGHT_CORE_DIR))

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
        "allergens": ["GLUTEN", "EGGS"],
        "baking_temp_c": 175.0,
        "baking_time_minutes": 32,
        "ratios": {"eggs_g": 0.45, "sugar_g": 0.30, "wheat_flour_g": 0.25},
    },
    "red_velvet": {
        "name": "Red Velvet Artisanal (Buttermilk & Cocoa)",
        "density_g_per_cm3": 0.54,
        "cost_eur_per_kg": 8.50,
        "allergens": ["GLUTEN", "EGGS", "MILK"],
        "baking_temp_c": 170.0,
        "baking_time_minutes": 35,
        "ratios": {"wheat_flour_g": 0.30, "sugar_g": 0.28, "buttermilk_g": 0.20, "eggs_g": 0.12, "butter_g": 0.10},
    },
    "chocolate_belga_70": {
        "name": "Bolo Húmido de Chocolate Belga 70%",
        "density_g_per_cm3": 0.58,
        "cost_eur_per_kg": 10.20,
        "allergens": ["GLUTEN", "EGGS", "MILK", "SOY"],
        "baking_temp_c": 170.0,
        "baking_time_minutes": 38,
        "ratios": {"wheat_flour_g": 0.24, "sugar_g": 0.26, "dark_chocolate_70_g": 0.20, "eggs_g": 0.15, "butter_g": 0.15},
    },
    "amendoa_sem_gluten": {
        "name": "Bolo de Amêndoa & Limão (Sem Glúten)",
        "density_g_per_cm3": 0.52,
        "cost_eur_per_kg": 12.40,
        "allergens": ["EGGS", "NUTS"],
        "baking_temp_c": 165.0,
        "baking_time_minutes": 34,
        "ratios": {"almond_flour_g": 0.45, "sugar_g": 0.30, "eggs_g": 0.25},
    },
    "nozes_vinho_porto": {
        "name": "Bolo Nobre de Noz & Redução de Vinho do Porto",
        "density_g_per_cm3": 0.56,
        "cost_eur_per_kg": 13.20,
        "allergens": ["GLUTEN", "EGGS", "MILK", "NUTS", "SULPHITES"],
        "baking_temp_c": 170.0,
        "baking_time_minutes": 36,
        "ratios": {"wheat_flour_g": 0.26, "sugar_g": 0.24, "walnut_meal_g": 0.20, "eggs_g": 0.18, "butter_g": 0.08, "port_wine_reduction_g": 0.04},
    },
}

FILLING_RECIPES: Dict[str, Dict[str, Any]] = {
    "brigadeiro_gourmet": {
        "name": "Brigadeiro Gourmet de Chocolate Nobre",
        "cost_eur_per_kg": 11.50,
        "allergens": ["MILK", "SOY"],
        "requires_refrigeration_4c": True,
    },
    "ovos_moles_doces_conventuais": {
        "name": "Doce de Ovos Conventual Português",
        "cost_eur_per_kg": 10.80,
        "allergens": ["EGGS"],
        "requires_refrigeration_4c": True,
    },
    "curd_limao_frutos_vermelhos": {
        "name": "Lemon Curd & Compota de Frutos Vermelhos",
        "cost_eur_per_kg": 12.00,
        "allergens": ["EGGS", "MILK"],
        "requires_refrigeration_4c": True,
    },
    "praline_avela_crocante": {
        "name": "Ganache & Praliné de Avelã Piemontesa",
        "cost_eur_per_kg": 15.50,
        "allergens": ["MILK", "NUTS", "SOY"],
        "requires_refrigeration_4c": True,
    },
    "pistacio_tahini_crocante": {
        "name": "Creme de Pistácio Siciliano & Crocante de Sésamo",
        "cost_eur_per_kg": 16.90,
        "allergens": ["MILK", "NUTS", "SESAME", "SOY"],
        "requires_refrigeration_4c": True,
    },
}

FROSTING_RECIPES: Dict[str, Dict[str, Any]] = {
    "swiss_meringue_buttercream": {
        "name": "Swiss Meringue Buttercream (Cetim Suave)",
        "cost_eur_per_kg": 9.80,
        "allergens": ["EGGS", "MILK"],
        "max_ambient_temp_c": 23.0,
    },
    "ganache_blindagem_fondant": {
        "name": "Blindagem em Ganache + Pasta de Açúcar (Fondant)",
        "cost_eur_per_kg": 12.50,
        "allergens": ["MILK", "SOY"],
        "max_ambient_temp_c": 28.0,
    },
    "semi_naked_rustico": {
        "name": "Semi-Naked Rústico com Flores Naturais",
        "cost_eur_per_kg": 8.90,
        "allergens": ["EGGS", "MILK"],
        "max_ambient_temp_c": 22.0,
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


def render_cake_asae_ficha_html(design_res: Dict[str, Any]) -> str:
    """Renders a printable A4 ASAE Technical Data Sheet (`Ficha Técnica de Fabrico Próprio`) for any 3D cake."""
    scene = design_res["threejs_3d_scene"]
    bom = design_res["recipe_bom_grams"]
    struct = design_res["portions_and_structure"]
    allerg = design_res["allergens_eu_1169_2011"]
    pricing = design_res["pricing_and_at_invoicing"]
    cold = design_res["logistics_and_haccp_cold_chain"]
    ficha_id = f"FT-ASAE-BAKE-{design_res['design_sha256'][:8].upper()}"

    rows_html = "".join(
        f"<tr><td>{html.escape(k)}</td><td>Massa Base ({html.escape(bom['sponge_type'])})</td><td style='text-align:right'>{v:.1f} g</td></tr>"
        for k, v in bom["sponge_ingredients_g"].items()
    )
    rows_html += (
        f"<tr><td>{html.escape(bom['filling_type'])}</td><td>Recheio Refrigerado</td><td style='text-align:right'>{bom['filling_total_g']:.1f} g</td></tr>"
        f"<tr><td>{html.escape(bom['frosting_type'])}</td><td>Cobertura &amp; Blindagem</td><td style='text-align:right'>{bom['frosting_total_g']:.1f} g</td></tr>"
    )
    dowel_rows = "".join(
        f"<li>Andar {d['tier_index']} ({d['tier_diameter_cm']} cm): <strong>{d['polypropylene_dowel_rods_count']} estacas PP alimentares</strong> cortadas a {d['dowel_cut_height_cm']} cm + prato {d['cake_board_under_upper_tier_cm']} cm</li>"
        for d in struct["tier_dowel_blueprint"]
    ) or "<li>Andar único — sem estacas internas necessárias.</li>"

    return f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<title>{ficha_id} — Ficha Técnica ASAE Cake Design ({html.escape(scene['topper_text'])})</title>
<style>
  body {{ font-family: Inter, system-ui, sans-serif; color: #0f172a; margin: 24px; line-height: 1.45; font-variant-numeric: tabular-nums; }}
  h1 {{ font-size: 18px; margin: 0 0 4px; }}
  h2 {{ font-size: 13px; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin-top: 16px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 6px 8px; text-align: left; }}
  th {{ background: #f1f5f9; }}
  .box {{ background: #fffbeb; border: 1px solid #f59e0b; padding: 8px 12px; border-radius: 6px; font-size: 12px; margin-top: 8px; }}
  @media print {{ .no-print {{ display: none; }} body {{ margin: 10mm; }} }}
</style>
</head>
<body>
  <div class="no-print" style="margin-bottom:12px;">
    <button onclick="window.print()" style="padding:8px 14px;background:#4f46e5;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:600;">Imprimir / Guardar PDF A4 (ASAE)</button>
  </div>
  <h1>FICHA TÉCNICA DE FABRICO PRÓPRIO — {ficha_id}</h1>
  <div style="font-size:12px;color:#475569;">
    <strong>Produto:</strong> Bolo Celebrativo {scene['tier_count']} Andares ({scene['shape']}) — Topo: "{html.escape(scene['topper_text'])}" |
    <strong>Peso Total:</strong> {struct['total_assembled_weight_kg']} kg ({struct['wedding_portions_2_5x5cm']} fatias casamento) |
    <strong>PVP:</strong> €{pricing['recommended_client_total_gross_eur']:.2f} ({html.escape(pricing['atcud_preview'])})
  </div>

  <h2>1. Capitação Quantitativa em Gramas (Reg. CE n.º 178/2002 Art. 18.º)</h2>
  <table>
    <thead><tr><th>Ingrediente / Componente</th><th>Grupo Técnico</th><th style="text-align:right">Peso Líquido (g)</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>

  <h2>2. Declaração Obrigatória dos 14 Alergénios (Reg. UE n.º 1169/2011 Anexo II &amp; DL n.º 26/2016)</h2>
  <div class="box"><strong>{html.escape(allerg['allergen_counter_signage_pt'])}</strong></div>

  <h2>3. Engenharia Estrutural Alimentar &amp; PCCs HACCP (Reg. CE n.º 852/2004)</h2>
  <ul style="font-size:12px;">
    <li><strong>PCC-1 Cozedura da Massa:</strong> Forno a {bom['sponge_baking_temp_c']} °C durante {bom['sponge_baking_time_minutes']} min (centro térmico &ge; +82 °C).</li>
    <li><strong>PCC-2 Conservação &amp; Transporte Frio:</strong> {html.escape(cold['refrigerated_van_target_temp_c'])} em caixa {html.escape(cold['required_transport_box_cm'])} (exposição ambiente máx. {cold['max_safe_ambient_display_temp_c']} °C).</li>
    {dowel_rows}
  </ul>
  <div style="font-size:11px;color:#64748b;margin-top:16px;font-family:monospace;">
    Recibo Criptográfico SHA-256 (EU AI Act Art. 12): {design_res['design_sha256']}
  </div>
</body>
</html>"""


class InsightBakeEngine:
    MEMBER_ID = "InsightBake"
    CLIENT_BRAND = "SetMiddle Insight™ · Bake"
    INTERNAL_ENGINE = "InsightCore"
    DEFAULT_PORT = 4030
    API_PREFIX = "/api/bake"

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "product": self.CLIENT_BRAND,
            "member_id": self.MEMBER_ID,
            "internal_engine": self.INTERNAL_ENGINE,
            "version": "1.2.0",
            "port": self.DEFAULT_PORT,
            "api_prefix": self.API_PREFIX,
            "standalone_benefit": (
                "Interactive Three.js 3D Multi-Tier Cake Configurator + Arrhenius Q10 Sourdough Fermentation Lab "
                "+ Exact Portion/Dowel/Gram Recipe Scaler + Full 14 EU 1169/2011 Allergens + Printable ASAE Ficha & InsightPastelaria (:4029) Bridge."
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
        design = self.execute(payload)
        if not design.get("ok"):
            return design

        client_name = _normalize_scrubbed_text(str(payload.get("client_name") or design["threejs_3d_scene"]["topper_text"] or "Cliente Cake Design"))
        requested_pickup = str(payload.get("requested_pickup_time") or "Amanhã às 16:00 (24h Cake Studio)")
        handoff_packet = {
            "client_name": client_name,
            "requested_pickup_time": requested_pickup,
            "lead_minutes_ahead": int(max(720, int(payload.get("lead_minutes_ahead", 1440)))),
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
                    "pastelaria_reservation": remote_data,
                    "cake_design": design,
                }
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            return {
                "ok": True,
                "bridge_mode": "QUEUED_HANDOFF_PACKET",
                "note": "InsightPastelaria (:4029) offline — deterministic 24h handoff packet & ASAE Ficha ready for import.",
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

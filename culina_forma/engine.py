"""
Canonical `culina_forma.engine` module — re-exports `CulinaFormaEngine`, 3D Food Design geometry,
Arrhenius Q10 fermentation kinetics, ASAE Ficha Técnica builders, and locale-ready fiscal helpers.
"""

from insight_bake.engine import *  # noqa: F401,F403
from insight_bake.engine import (
    EU_14_MANDATORY_ALLERGENS,
    FILLING_RECIPES,
    FROSTING_RECIPES,
    SPONGE_RECIPES,
    CulinaFormaEngine,
    InsightBakeEngine,
    build_bake_asae_ficha_tecnica,
    build_culina_forma_asae_ficha_tecnica,
    compute_arrhenius_fermentation_and_bakers_pct,
    design_3d_cake_and_production_sheet,
    render_cake_asae_ficha_html,
    render_cake_asae_ficha_pdf_bytes,
    validate_portuguese_nif_modulo11,
)

__all__ = [
    "EU_14_MANDATORY_ALLERGENS",
    "SPONGE_RECIPES",
    "FILLING_RECIPES",
    "FROSTING_RECIPES",
    "CulinaFormaEngine",
    "InsightBakeEngine",
    "design_3d_cake_and_production_sheet",
    "compute_arrhenius_fermentation_and_bakers_pct",
    "build_culina_forma_asae_ficha_tecnica",
    "build_bake_asae_ficha_tecnica",
    "render_cake_asae_ficha_html",
    "render_cake_asae_ficha_pdf_bytes",
    "validate_portuguese_nif_modulo11",
]

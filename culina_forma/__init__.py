"""
`CulinaForma™` (`culina_forma`) — Sovereign 3D Food Design, Structural Multi-Tier Cake Engineering,
Arrhenius Q10 Fermentation & ASAE/HACCP Studio (`:4030 /api/culinaforma`).

Re-exports the full engine and FastAPI router while maintaining 100% backward compatibility
with `insight_bake` (`/api/bake`).
"""

from insight_bake import (
    EU_14_MANDATORY_ALLERGENS,
    FILLING_RECIPES,
    FROSTING_RECIPES,
    SPONGE_RECIPES,
    CulinaFormaEngine,
    InsightBakeEngine,
    __version__,
    create_culina_forma_router,
    create_insight_bake_router,
    design_3d_cake_and_production_sheet,
    mount_culina_forma_plugin,
    mount_insight_bake_plugin,
)

__all__ = [
    "__version__",
    "EU_14_MANDATORY_ALLERGENS",
    "SPONGE_RECIPES",
    "FILLING_RECIPES",
    "FROSTING_RECIPES",
    "CulinaFormaEngine",
    "InsightBakeEngine",
    "design_3d_cake_and_production_sheet",
    "create_culina_forma_router",
    "create_insight_bake_router",
    "mount_culina_forma_plugin",
    "mount_insight_bake_plugin",
]

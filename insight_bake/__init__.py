"""
`CulinaForma™` (`CulinaForma` — `:4030 /api/culinaforma`, backward-compatible `insight_bake` / `/api/bake`) —
3D Food Design, Structural Cake Engineering & Arrhenius Formulation Studio powered by `InsightCore™`.
"""

from insight_bake.engine import (
    EU_14_MANDATORY_ALLERGENS,
    SPONGE_RECIPES,
    FILLING_RECIPES,
    FROSTING_RECIPES,
    CulinaFormaEngine,
    InsightBakeEngine,
    design_3d_cake_and_production_sheet,
)
from insight_bake.router import (
    create_culina_forma_router,
    create_insight_bake_router,
    mount_culina_forma_plugin,
    mount_insight_bake_plugin,
)

__version__ = "1.9.0"

__all__ = [
    "EU_14_MANDATORY_ALLERGENS",
    "SPONGE_RECIPES",
    "FILLING_RECIPES",
    "FROSTING_RECIPES",
    "CulinaFormaEngine",
    "InsightBakeEngine",
    "design_3d_cake_and_production_sheet",
    "__version__",
    "create_culina_forma_router",
    "create_insight_bake_router",
    "mount_culina_forma_plugin",
    "mount_insight_bake_plugin",
]

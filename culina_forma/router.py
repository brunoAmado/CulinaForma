"""
Canonical `culina_forma.router` module — mounts `/api/culinaforma` (and backward-compatible `/api/bake`).
"""

from insight_bake.router import (
    INTERACTIVE_3D_CAKE_STUDIO_HTML,
    create_culina_forma_router,
    create_insight_bake_router,
    mount_culina_forma_plugin,
    mount_insight_bake_plugin,
)

__all__ = [
    "INTERACTIVE_3D_CAKE_STUDIO_HTML",
    "create_culina_forma_router",
    "create_insight_bake_router",
    "mount_culina_forma_plugin",
    "mount_insight_bake_plugin",
]

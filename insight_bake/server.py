"""
Standalone FastAPI Server for `CulinaForma™` (`python -m culina_forma.server` / `python -m insight_bake.server`).
Runs on port 4030 by default, exposing canonical `/api/culinaforma` and backward-compatible `/api/bake`.
"""

import os
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from insight_bake.router import INTERACTIVE_3D_CAKE_STUDIO_HTML, mount_culina_forma_plugin

app = FastAPI(
    title="CulinaForma™ — Three.js 3D Multi-Tier Food & Cake Studio, ComfyUI ControlNet Lock, Recipe BOM & HACCP Cold-Chain Logistics (Powered by InsightCore)",
    version="1.9.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

mount_culina_forma_plugin(app, prefix="/api/culinaforma")
mount_culina_forma_plugin(app, prefix="/api/bake")


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def standalone_project_dashboard() -> HTMLResponse:
    """Serves the standalone UX Engine 2.8 & WCAG 2.2 AA/AAA webpage & interactive 3D Food Design Studio."""
    ic_dir = "C:/Users/bruno/PycharmProjects/InsightCore"
    if Path(ic_dir).exists() and ic_dir not in sys.path:
        sys.path.insert(0, ic_dir)
    try:
        from insight_core.dashboard_ui import render_standalone_project_dashboard_html
        return HTMLResponse(content=render_standalone_project_dashboard_html("CulinaForma", host_mode="STANDALONE"))
    except Exception:
        return HTMLResponse(content=INTERACTIVE_3D_CAKE_STUDIO_HTML)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "CulinaForma",
        "legacy_alias": "InsightBake",
        "client_brand": "CulinaForma",
        "internal_engine": "InsightCore",
        "port": 4030,
        "api_prefix": "/api/culinaforma",
        "legacy_api_prefix": "/api/bake",
        "version": "1.9.0",
    }


def main() -> None:
    port = int(os.environ.get("PORT", "4030"))
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()

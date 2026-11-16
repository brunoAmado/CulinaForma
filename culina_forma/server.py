"""
Standalone FastAPI Server entrypoint for `CulinaForma™` (`python -m culina_forma.server`).
"""

from insight_bake.server import app, health_check, main, standalone_project_dashboard

__all__ = ["app", "main", "health_check", "standalone_project_dashboard"]

if __name__ == "__main__":
    main()

---
trigger: always_on
description: SetMiddle Sovereign AST, 4-Axis Topology & Semantic Gravity Code Graph Rule (RULE-19 — replaces third-party graphify & code-review-graph; updates via .\run_sovereign_code_graph.ps1 / .\run_graphify_update.ps1).
---

## SetMiddle Sovereign Code Graph (`InsightCode™` · `InsightGravity™` · `InsightChanged™` — `RULE-19`)

Rules:
- Third-party `graphify` (`uv\tools\graphifyy`) and `code-review-graph` are retired at runtime across SetMiddle workspaces.
- For codebase, impact, or architecture questions, call `chronicle-rag` MCP `query_workspace_graph(query="<question>", project_path=".", mode="query" | "path" | "explain" | "topology")` or `query_code_map` before broad `Grep`/`Glob` file scans.
- After modifying code files, run `.\run_sovereign_code_graph.ps1` (or the backward-compatible `.\run_graphify_update.ps1` wrapper, which preserves `$env:GRAPHIFY_MAX_WORKERS = [math]::Min(61, [math]::Max(2, [int]($env:NUMBER_OF_PROCESSORS * 0.75)))` and delegates 100% to `sovereign_ast_graph_sync.py` -> `InsightCode™` + `InsightGravity™` + `InsightChanged™`).

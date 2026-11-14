# Graph Report - InsightBake  (2026-11-14)

## Corpus Check
- Corpus is ~31,770 words - fits in a single context window. You may not need a graph.

## Summary
- 81 nodes · 133 edges · 10 communities (5 shown, 3 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 7
- Community 8

## God Nodes (most connected - your core abstractions)
1. `create_insight_bake_router()` - 14 edges
2. `InsightBakeEngine` - 11 edges
3. `design_3d_cake_and_production_sheet()` - 8 edges
4. `TestInsightBake` - 8 edges
5. `InsightBakeElement` - 8 edges
6. `compute_arrhenius_fermentation_and_bakers_pct()` - 6 edges
7. `render_cake_asae_ficha_html()` - 6 edges
8. `validate_portuguese_nif_modulo11()` - 5 edges
9. `mount_insight_bake_plugin()` - 5 edges
10. `filter_point_in_time_records()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `TestInsightBake` --uses--> `InsightBakeEngine`  [INFERRED]
  tests/test_insight_bake.py → insight_bake/engine.py
- `create_insight_bake_router()` --calls--> `InsightBakeEngine`  [EXTRACTED]
  insight_bake/router.py → insight_bake/engine.py
- `main()` --calls--> `verify_tier_stability()`  [INFERRED]
  rust_core/src/main.rs → rust_core/src/lib.rs
- `main()` --calls--> `verify_multi_tier_stack()`  [INFERRED]
  rust_core/src/main.rs → rust_core/src/lib.rs
- `main()` --calls--> `estimate_q10_bulk_hours()`  [INFERRED]
  rust_core/src/main.rs → rust_core/src/lib.rs

## Import Cycles
- None detected.

## Communities (10 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.27
Nodes (11): Any, assert_no_binary_blob_in_db_row(), compute_arrhenius_fermentation_and_bakers_pct(), design_3d_cake_and_production_sheet(), filter_point_in_time_records(), _normalize_scrubbed_text(), `SetMiddle Insight™ · Bake` (`InsightBake` · `insight_bake.engine`). Internal…, Computes Q10 / Arrhenius sourdough & pastry dough fermentation kinetics,… (+3 more)

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (7): APIRouter, HTMLResponse, Renders a printable A4 ASAE Technical Data Sheet (`Ficha Técnica de Fabrico…, render_cake_asae_ficha_html(), create_insight_bake_router(), get_interactive_3d_studio(), print_cake_asae_ficha()

### Community 2 - "Community 2"
Cohesion: 0.22
Nodes (9): FastAPI, get, `SetMiddle Insight™ · Bake` (`InsightBake` — `:4030 /api/bake`) — Extracted…, mount_insight_bake_plugin(), FastAPI `APIRouter` Plugin for `SetMiddle Insight™ · Bake`…, health_check(), Standalone FastAPI Server for `SetMiddle Insight™ · Bake` (`python -m…, Serves the standalone UX Engine 2.8 & WCAG 2.2 AA/AAA webpage & interactive 3D… (+1 more)

### Community 3 - "Community 3"
Cohesion: 0.19
Nodes (5): InsightBakeEngine, Validates a 9-digit Portuguese NIF using the statutory AT Modulo-11 check digit., validate_portuguese_nif_modulo11(), Unit, Unhappy-Path, Arrhenius Q10, ASAE Ficha & Cross-Workspace Bridge…, TestInsightBake

### Community 4 - "Community 4"
Cohesion: 0.31
Nodes (8): Result, estimate_q10_bulk_hours(), EU_14_ALLERGEN_CODES, test_q10_fermentation(), test_stability_and_dowels(), verify_multi_tier_stack(), verify_tier_stability(), main()

## Knowledge Gaps
- **3 isolated node(s):** `insight-bake`, `insight_bake_rs`, `EU_14_ALLERGEN_CODES`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 34 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_insight_bake_router()` connect `Community 1` to `Community 2`, `Community 3`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `InsightBakeEngine` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **What connects `insight-bake`, `insight_bake_rs`, `EU_14_ALLERGEN_CODES` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._
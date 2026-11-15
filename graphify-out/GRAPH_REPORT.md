# Graph Report - InsightBake  (2026-11-15)

## Corpus Check
- Corpus is ~47,167 words - fits in a single context window. You may not need a graph.

## Summary
- 167 nodes · 287 edges · 12 communities (6 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10

## God Nodes (most connected - your core abstractions)
1. `create_insight_bake_router()` - 35 edges
2. `InsightBakeEngine` - 31 edges
3. `TestInsightBake` - 14 edges
4. `design_3d_cake_and_production_sheet()` - 13 edges
5. `_normalize_scrubbed_text()` - 10 edges
6. `build_bake_asae_ficha_tecnica()` - 9 edges
7. `render_cake_asae_ficha_html()` - 8 edges
8. `mount_insight_bake_plugin()` - 8 edges
9. `InsightBakeElement` - 8 edges
10. `compute_arrhenius_fermentation_and_bakers_pct()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `TestInsightBake` --uses--> `InsightBakeEngine`  [INFERRED]
  tests/test_insight_bake.py → insight_bake/engine.py
- `create_insight_bake_router()` --calls--> `render_cake_asae_ficha_html()`  [EXTRACTED]
  insight_bake/router.py → insight_bake/engine.py
- `print_cake_asae_ficha()` --calls--> `render_cake_asae_ficha_html()`  [EXTRACTED]
  insight_bake/router.py → insight_bake/engine.py
- `create_insight_bake_router()` --calls--> `InsightBakeEngine`  [EXTRACTED]
  insight_bake/router.py → insight_bake/engine.py
- `main()` --calls--> `verify_tier_stability()`  [INFERRED]
  rust_core/src/main.rs → rust_core/src/lib.rs

## Import Cycles
- None detected.

## Communities (12 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.11
Nodes (18): Any, assert_no_binary_blob_in_db_row(), InsightBakeEngine, _render_worker(), _normalize_scrubbed_text(), Path, Unified PostgreSQL 17 (`:5432/chroniclerag`, Zero Runtime `ChromaDB` per…, Creates a 50% deposit payment intent (`MBWAY` or `MULTIBANCO` Modulo-97) for a… (+10 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (7): APIRouter, HTMLResponse, create_insight_bake_router(), _build_query_payload(), download_cake_asae_ficha_pdf_get(), get_interactive_3d_studio(), print_cake_asae_ficha()

### Community 2 - "Community 2"
Cohesion: 0.17
Nodes (11): FastAPI, get, `SetMiddle Insight™ · Bake` (`InsightBake` — `:4030 /api/bake`) — Extracted…, mount_insight_bake_plugin(), Path, FastAPI `APIRouter` Plugin for `SetMiddle Insight™ · Bake`…, health_check(), Standalone FastAPI Server for `SetMiddle Insight™ · Bake` (`python -m… (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.18
Nodes (14): compute_arrhenius_fermentation_and_bakers_pct(), compute_eu_1169_nutritional_declaration(), compute_thermal_melt_countdown(), design_3d_cake_and_production_sheet(), filter_point_in_time_records(), format_multibanco_ref_mod97(), `SetMiddle Insight™ · Bake` (`InsightBake` · `insight_bake.engine`). Internal…, Generates a deterministic Portuguese SIBS Multibanco 9-digit reference (`XXX… (+6 more)

### Community 4 - "Community 4"
Cohesion: 0.20
Nodes (11): Result, compute_eu1169_energy_per_100g(), estimate_q10_bulk_hours(), EU_14_ALLERGEN_CODES, format_multibanco_ref_mod97(), test_q10_nutrition_multibanco_and_fleet(), test_stability_and_dowels(), verify_multi_tier_stack() (+3 more)

### Community 7 - "Community 7"
Cohesion: 0.22
Nodes (9): ASAEEstablishmentProfile, ASAEFichaTecnica, build_bake_asae_ficha_tecnica(), Renders the complete `MOD-FT-ASAE-DGAV-ACIP-v2.0` Official ASAE A4 HTML Sheet…, Renders a native Vector A4 Portrait PDF (`MOD-FT-ASAE-DGAV-ACIP-v2.0`) for any…, Generates the A4 Landscape Counter Allergen Matrix PDF (`DL n.º 26/2016`) for…, Converts any `InsightBake` 3D Multi-Tier Cake Design…, render_cake_asae_ficha_html() (+1 more)

## Knowledge Gaps
- **3 isolated node(s):** `insight-bake`, `insight_bake_rs`, `EU_14_ALLERGEN_CODES`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 87 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InsightBakeEngine` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.254) - this node is a cross-community bridge._
- **Why does `create_insight_bake_router()` connect `Community 1` to `Community 0`, `Community 2`, `Community 7`?**
  _High betweenness centrality (0.237) - this node is a cross-community bridge._
- **Why does `TestInsightBake` connect `Community 6` to `Community 0`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **What connects `insight-bake`, `insight_bake_rs`, `EU_14_ALLERGEN_CODES` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.10609756097560975 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07096774193548387 - nodes in this community are weakly interconnected._
- **Should `Community 5` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
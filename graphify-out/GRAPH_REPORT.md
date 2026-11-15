# Graph Report - InsightBake  (2026-11-15)

## Corpus Check
- 48 files · ~53,032 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .feature 1)

## Summary
- 199 nodes · 338 edges · 15 communities (8 shown, 5 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13

## God Nodes (most connected - your core abstractions)
1. `create_insight_bake_router()` - 44 edges
2. `InsightBakeEngine` - 41 edges
3. `TestInsightBake` - 17 edges
4. `design_3d_cake_and_production_sheet()` - 13 edges
5. `_normalize_scrubbed_text()` - 11 edges
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

## Communities (15 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (7): APIRouter, HTMLResponse, create_insight_bake_router(), _build_query_payload(), download_cake_asae_ficha_pdf_get(), get_interactive_3d_studio(), print_cake_asae_ficha()

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (12): FastAPI, get, Validates a 9-digit Portuguese NIF using the statutory AT Modulo-11 check digit., validate_portuguese_nif_modulo11(), mount_insight_bake_plugin(), Path, health_check(), Standalone FastAPI Server for `SetMiddle Insight™ · Bake` (`python -m… (+4 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (22): ASAEEstablishmentProfile, ASAEFichaTecnica, build_bake_asae_ficha_tecnica(), compute_arrhenius_fermentation_and_bakers_pct(), compute_eu_1169_nutritional_declaration(), compute_thermal_melt_countdown(), design_3d_cake_and_production_sheet(), filter_point_in_time_records() (+14 more)

### Community 3 - "Community 3"
Cohesion: 0.21
Nodes (5): Any, InsightBakeEngine, Semantic & constraint-aware recipe discovery (`RULE-16` Zero `ChromaDB` —…, Reverse Guest-Count & Budget Solver: searches multi-tier geometries and recipe…, scrub_pt_eu_pii_and_byok_secrets()

### Community 5 - "Community 5"
Cohesion: 0.17
Nodes (11): Result, compute_eu1169_energy_per_100g(), estimate_q10_bulk_hours(), EU_14_ALLERGEN_CODES, format_multibanco_ref_mod97(), test_q10_nutrition_multibanco_and_fleet(), test_stability_and_dowels(), verify_multi_tier_stack() (+3 more)

### Community 6 - "Community 6"
Cohesion: 0.17
Nodes (5): Unified PostgreSQL 17 (`:5432/chroniclerag`, Zero Runtime `ChromaDB` per…, Creates a 50% deposit payment intent (`MBWAY` or `MULTIBANCO` Modulo-97) for a…, Registers a refundable security deposit (`Caução de Suporte / Pedestal`) in…, Settles a reusable stand security deposit (`Caução`): - Intact return -> 100%…, Deterministically reformulates a 3D multi-tier cake for strict dietary regimes:…

### Community 7 - "Community 7"
Cohesion: 0.20
Nodes (6): assert_no_binary_blob_in_db_row(), _render_worker(), Non-blocking asynchronous `ComfyUI` ControlNet Depth/Canny render job queue…, Generates the A4 Landscape Counter Allergen Matrix PDF (`DL n.º 26/2016`) for…, Creates a zero-PII shareable Client Quote Approval Portal token (`QT-BAKE-*`)., Dispatches a multi-tier cake via `InsightFleet` (`:4026`), enforcing cold-chain…

### Community 8 - "Community 8"
Cohesion: 0.20
Nodes (5): _normalize_scrubbed_text(), Exports a locale-ready `SAF-T v1.04_01` SalesInvoice XML snippet supporting any…, Executes a 3D Cake Design or Arrhenius Q10 Fermentation calculation, builds its…, Designs the 3D cake, builds the `day_before` (`24h`) production & ASAE handoff…, Books a 4-Flavor Tasting Box (`Caixa de Prova de Sabores`) and issues a…

## Knowledge Gaps
- **3 isolated node(s):** `insight-bake`, `insight_bake_rs`, `EU_14_ALLERGEN_CODES`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 109 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InsightBakeEngine` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 6`, `Community 7`, `Community 8`, `Community 10`, `Community 11`?**
  _High betweenness centrality (0.295) - this node is a cross-community bridge._
- **Why does `create_insight_bake_router()` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.262) - this node is a cross-community bridge._
- **Why does `TestInsightBake` connect `Community 1` to `Community 3`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **What connects `insight-bake`, `insight_bake_rs`, `EU_14_ALLERGEN_CODES` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05384615384615385 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.08045977011494253 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.13 - nodes in this community are weakly interconnected._
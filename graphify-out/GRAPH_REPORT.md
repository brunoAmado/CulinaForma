# Graph Report - InsightBake  (2026-11-15)

## Corpus Check
- Corpus is ~39,559 words - fits in a single context window. You may not need a graph.

## Summary
- 110 nodes · 185 edges · 16 communities (9 shown, 5 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14

## God Nodes (most connected - your core abstractions)
1. `create_insight_bake_router()` - 21 edges
2. `InsightBakeEngine` - 16 edges
3. `build_bake_asae_ficha_tecnica()` - 9 edges
4. `TestInsightBake` - 9 edges
5. `design_3d_cake_and_production_sheet()` - 8 edges
6. `render_cake_asae_ficha_html()` - 8 edges
7. `mount_insight_bake_plugin()` - 8 edges
8. `InsightBakeElement` - 8 edges
9. `compute_arrhenius_fermentation_and_bakers_pct()` - 6 edges
10. `render_cake_asae_ficha_pdf_bytes()` - 6 edges

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

## Communities (16 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (8): APIRouter, HTMLResponse, create_insight_bake_router(), _build_query_payload(), download_cake_asae_ficha_pdf_get(), get_interactive_3d_studio(), print_cake_asae_ficha(), Path

### Community 1 - "Community 1"
Cohesion: 0.21
Nodes (9): FastAPI, get, mount_insight_bake_plugin(), FastAPI `APIRouter` Plugin for `SetMiddle Insight™ · Bake`…, health_check(), Standalone FastAPI Server for `SetMiddle Insight™ · Bake` (`python -m…, Serves the standalone UX Engine 2.8 & WCAG 2.2 AA/AAA webpage & interactive 3D…, standalone_project_dashboard() (+1 more)

### Community 2 - "Community 2"
Cohesion: 0.24
Nodes (11): Result, compute_eu1169_energy_per_100g(), estimate_q10_bulk_hours(), EU_14_ALLERGEN_CODES, format_multibanco_ref_mod97(), test_q10_nutrition_and_multibanco(), test_stability_and_dowels(), verify_multi_tier_stack() (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.25
Nodes (8): compute_arrhenius_fermentation_and_bakers_pct(), compute_eu_1169_nutritional_declaration(), filter_point_in_time_records(), format_multibanco_ref_mod97(), `SetMiddle Insight™ · Bake` (`InsightBake` · `insight_bake.engine`). Internal…, Generates a deterministic Portuguese SIBS Multibanco 9-digit reference (`XXX…, Computes the statutory EU Regulation No. 1169/2011 Art. 30.º & Annex XIV…, Computes Q10 / Arrhenius sourdough & pastry dough fermentation kinetics,…

### Community 4 - "Community 4"
Cohesion: 0.22
Nodes (3): Validates a 9-digit Portuguese NIF using the statutory AT Modulo-11 check digit., validate_portuguese_nif_modulo11(), TestInsightBake

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (8): ASAEEstablishmentProfile, ASAEFichaTecnica, build_bake_asae_ficha_tecnica(), Renders the complete `MOD-FT-ASAE-DGAV-ACIP-v2.0` Official ASAE A4 HTML Sheet…, Renders a native Vector A4 Portrait PDF (`MOD-FT-ASAE-DGAV-ACIP-v2.0`) for any…, Converts any `InsightBake` 3D Multi-Tier Cake Design…, render_cake_asae_ficha_html(), render_cake_asae_ficha_pdf_bytes()

### Community 7 - "Community 7"
Cohesion: 0.48
Nodes (3): Any, InsightBakeEngine, scrub_pt_eu_pii_and_byok_secrets()

### Community 8 - "Community 8"
Cohesion: 0.40
Nodes (3): _normalize_scrubbed_text(), Executes a 3D Cake Design or Arrhenius Q10 Fermentation calculation, builds its…, Designs the 3D cake, builds the `day_before` (`24h`) production & ASAE handoff…

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): design_3d_cake_and_production_sheet(), Computes the complete `Three.js` 3D scene graph, wedding/party portions,…, `SetMiddle Insight™ · Bake` (`InsightBake` — `:4030 /api/bake`) — Extracted…

## Knowledge Gaps
- **3 isolated node(s):** `insight-bake`, `insight_bake_rs`, `EU_14_ALLERGEN_CODES`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 47 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_insight_bake_router()` connect `Community 0` to `Community 1`, `Community 11`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.183) - this node is a cross-community bridge._
- **Why does `InsightBakeEngine` connect `Community 7` to `Community 0`, `Community 1`, `Community 3`, `Community 4`, `Community 8`, `Community 10`, `Community 11`, `Community 12`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Why does `TestInsightBake` connect `Community 4` to `Community 1`, `Community 7`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **What connects `insight-bake`, `insight_bake_rs`, `EU_14_ALLERGEN_CODES` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.13071895424836602 - nodes in this community are weakly interconnected._
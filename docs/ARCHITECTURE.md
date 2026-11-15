# 🏛️ InsightBake — System Architecture & Documentation (`v1.4.0`)

See the **[InsightBake Wiki](../wiki/Home.md)** for full navigation.

## Overview — `SetMiddle Insight™ · Bake` (`:4030 /api/bake`)

- **Company**: **SetMiddle** (`setmiddle.io` / `setmiddle.ai`)
- **Product Line**: **`SetMiddle Insight™ · Bake — 3D Cake Studio, Arrhenius Q10 Lab & ASAE Compliance`**
- **Internal Engine**: **`InsightCore`** (`insightCoreIO` + `insightCoreAI`)
- **4-Layer Polyglot Stack**:
  1. **Rust Structural, Fiscal & Nutritional Kernel (`rust_core/`)**: Memory-safe stacked tier stability (`verify_multi_tier_stack`), slenderness ratio guard (`H / D_base <= 2.2` optimal, `<= 2.6` ceiling), polypropylene dowel rod count, EU-14 allergen code table, Arrhenius $Q_{10}$ bulk fermentation kinetics (`estimate_q10_bulk_hours`), EU `Reg. 1169/2011 Art. 30.º` energy (`kJ`/`kcal`) calculation (`compute_eu1169_energy_per_100g`), and SIBS `Modulo-97` Multibanco reference formatting (`format_multibanco_ref_mod97`).
  2. **Python FastAPI Service & Mountable Router (`insight_bake/engine.py`, `router.py`, `server.py`)**:
     - Parametric `1..6` tier 3D scene graph supporting `ROUND` (`CylinderGeometry`), `SQUARE` (`BoxGeometry`), `HEART` (`ExtrudeHeartGeometry`), and `HEXAGON` (`6`-segment prism) with **Per-Tier Flavor Mixing** (`tiers[i].sponge_key` / `filling_key`) and **3D Cutaway Cross-Section Slice Layers** (`cutaway_layers`: 3 sponge discs + 2 filling bands per tier).
     - Exact gram-level BOM scaling, all **14 mandatory EU `Reg. (UE) n.º 1169/2011 Anexo II` allergens**, statutory **EU `Reg. 1169/2011 Art. 30.º` Nutritional Declaration** (`per_100g` & `per_portion`), Portuguese counter signage (`DL n.º 26/2016`), Modulo-11 NIF validation, and Portugal AT IVA regimes (`13%` *Restauração* vs. `23%` *Take-Away*) with `ATCUD`.
     - **SIBS `MB WAY` / `Multibanco` (`Modulo-97`) 50% Deposit State Machine & `SAF-T (PT) v1.04_01` XML Export**: `/deposit-checkout`, `/deposit-confirm`, and `/saft-pt-preview` (`DL n.º 28/2019`), backed by Unified PostgreSQL 17 (`:5432/chroniclerag`) dual-write + local JSON fallback (Zero `ChromaDB` per `RULE-16`).
     - **Non-Blocking Async `ComfyUI` Render Queue & Semantic/Allergen-Safe Search**: Abortable background ControlNet Z-depth render jobs (`POST /render-jobs`, `POST /render-jobs/{job_id}/cancel` — `RULE-10` & `EU AI Act Art. 14` with `cas://insight-bake/...` URI enforcement) and natural-language constraint search (`POST /search-recipes`).
     - **Arrhenius $Q_{10}$ Sourdough Fermentation & Baker's % Engine** (`/api/bake/fermentation`) with 3-factor Desired Dough Temperature (`DDT`) water calculation and bi-temporal ASAE HACCP lot traceability.
     - **Native Vector A4 ASAE PDFs (`MOD-FT-ASAE-DGAV-ACIP-v2.0`), 14-Allergen Counter Matrix & Establishment Sync**: `GET/POST /api/bake/ficha-asae/pdf` (for both 3D cakes `FT-ASAE-BAKE-*` and Arrhenius sourdough `FT-ASAE-FERM-*`), `GET /api/bake/fichas-tecnicas/caderno-alergenios.pdf`, `GET/PUT /api/bake/estabelecimento`, and **Live 24h Custom Cake Bridge** (`POST /api/bake/reserve-pastelaria` -> `InsightPastelaria :4029`).
  3. **Node.js / TypeScript SDK (`node_sdk/index.js`)**: `getBakeStatus`, `designCake3D`, `computeFermentation`, `reserveCustomCakeInPastelaria`, `createDepositCheckout`, `confirmDepositPayment`, `exportSaftPtPreview`, `submitAsyncComfyRenderJob`, and `searchSafeCakeRecipes`.
  4. **UX Engine 2.8 Studio & `<insight-bake>` Web Component (`ui_component/insight-bake.ts` & `/api/bake/studio`)**: Interactive `Three.js` WebGL viewport (with zero-dependency 2.5D isometric fallback, `🔪 Corte Transversal` cutaway slice toggle, and `🦴 Raio-X Estacas` dowel toggle), semantic search bar, roving `tabindex` modes, 1 Hero KPI + 3 secondary KPIs, and 4 async states (`WCAG 2.2 AA/AAA` & `DL n.º 82/2022`).

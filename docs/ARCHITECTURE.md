# 🏛️ InsightBake — System Architecture & Documentation (`v1.5.0`)

See the **[InsightBake Wiki](../wiki/Home.md)** for full navigation.

## Overview — `SetMiddle Insight™ · Bake` (`:4030 /api/bake`)

- **Company**: **SetMiddle** (`setmiddle.io` / `setmiddle.ai`)
- **Product Line**: **`SetMiddle Insight™ · Bake — 3D Cake Studio, Arrhenius Q10 Lab & ASAE Compliance`**
- **Internal Engine**: **`InsightCore`** (`insightCoreIO` + `insightCoreAI`)
- **4-Layer Polyglot Stack**:
  1. **Rust Structural, Fiscal, Nutritional & Fleet Kernel (`rust_core/`)**: Memory-safe stacked tier stability (`verify_multi_tier_stack`), slenderness ratio guard (`H / D_base <= 2.2` optimal, `<= 2.6` ceiling), polypropylene dowel rod count, EU-14 allergen code table, Arrhenius $Q_{10}$ bulk fermentation kinetics (`estimate_q10_bulk_hours`), EU `Reg. 1169/2011 Art. 30.º` energy (`kJ`/`kcal`) calculation, SIBS `Modulo-97` Multibanco reference formatting, summer thermal melt countdown (`estimate_out_of_fridge_safe_minutes`), and fleet cold-chain + G-force validation (`is_fleet_delivery_telemetry_safe`).
  2. **Python FastAPI Service & Mountable Router (`insight_bake/engine.py`, `router.py`, `server.py`)**:
     - Parametric `1..6` tier 3D scene graph supporting `ROUND` (`CylinderGeometry`), `SQUARE` (`BoxGeometry`), `HEART` (`ExtrudeHeartGeometry`), and `HEXAGON` (`6`-segment prism) with **Per-Tier Flavor Mixing**, **3D Cutaway Cross-Section Slice Layers**, and **Summer Thermal Melt Countdown** (`minutes_until_structural_softening`).
     - **Reverse Guest-Count & Budget Solver (`POST /solve-budget`)**, **4-Flavor Tasting Box (`Caixa de Prova` — `POST /tasting-box`)** with `100%` deposit credit vouchers, and **Zero-PII Shareable Client Quote Approval Portal** (`POST /quotes`, `GET /quotes/{quote_token}`, `POST /quotes/{quote_token}/approve`).
     - **Refrigerated Fleet Cold-Chain Dispatch, G-Force Guard (`<= 0.35g`), AT Transport Guide (`DL n.º 198/2012`) & `cas://` POD**: `POST /fleet-dispatch` and `POST /fleet-dispatch/{delivery_id}/pod`.
     - Exact gram-level BOM scaling, all **14 mandatory EU `Reg. (UE) n.º 1169/2011 Anexo II` allergens**, statutory **EU `Reg. 1169/2011 Art. 30.º` Nutritional Declaration** (`per_100g` & `per_portion`), Portuguese counter signage (`DL n.º 26/2016`), Modulo-11 NIF validation, and Portugal AT IVA regimes (`13%` *Restauração* vs. `23%` *Take-Away*) with `ATCUD`.
     - **SIBS `MB WAY` / `Multibanco` (`Modulo-97`) 50% Deposit State Machine & `SAF-T (PT) v1.04_01` XML Export**: `/deposit-checkout`, `/deposit-confirm`, and `/saft-pt-preview` (`DL n.º 28/2019`), backed by Unified PostgreSQL 17 (`:5432/chroniclerag`) dual-write + local JSON fallback (Zero `ChromaDB` per `RULE-16`).
     - **Non-Blocking Async `ComfyUI` Render Queue & Semantic/Allergen-Safe Search**: Abortable background ControlNet Z-depth render jobs (`POST /render-jobs`, `POST /render-jobs/{job_id}/cancel` — `RULE-10` & `EU AI Act Art. 14` with `cas://insight-bake/...` URI enforcement) and natural-language constraint search (`POST /search-recipes`).
     - **Arrhenius $Q_{10}$ Sourdough Fermentation & Baker's % Engine** (`/api/bake/fermentation`) + **Native Vector A4 ASAE PDFs (`MOD-FT-ASAE-DGAV-ACIP-v2.0`), 14-Allergen Counter Matrix, Establishment Sync & Live 24h `InsightPastelaria` (`:4029`) Bridge**.
  3. **Node.js / TypeScript SDK (`node_sdk/index.js`)**: `getBakeStatus`, `designCake3D`, `computeFermentation`, `reserveCustomCakeInPastelaria`, `createDepositCheckout`, `confirmDepositPayment`, `exportSaftPtPreview`, `submitAsyncComfyRenderJob`, `searchSafeCakeRecipes`, `solveCakeByGuestsAndBudget`, `createTastingBoxOrder`, `createShareableClientQuote`, and `dispatchRefrigeratedFleet`.
  4. **UX Engine 2.8 Studio & `<insight-bake>` Web Component (`ui_component/insight-bake.ts` & `/api/bake/studio`)**.

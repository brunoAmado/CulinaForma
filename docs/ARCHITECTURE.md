# 🏛️ InsightBake — System Architecture & Documentation (`v1.2.0`)

See the **[InsightBake Wiki](../wiki/Home.md)** for full navigation.

## Overview — `SetMiddle Insight™ · Bake` (`:4030 /api/bake`)

- **Company**: **SetMiddle** (`setmiddle.io` / `setmiddle.ai`)
- **Product Line**: **`SetMiddle Insight™ · Bake — 3D Cake Studio, Arrhenius Q10 Lab & ASAE Compliance`**
- **Internal Engine**: **`InsightCore`** (`insightCoreIO` + `insightCoreAI`)
- **4-Layer Polyglot Stack**:
  1. **Rust Structural & Fermentation Kernel (`rust_core/`)**: Memory-safe stacked tier stability (`verify_multi_tier_stack`), slenderness ratio guard (`H / D_base <= 2.2` optimal, `<= 2.6` ceiling), polypropylene dowel rod count, EU-14 allergen code table, and Arrhenius $Q_{10}$ bulk fermentation kinetics (`estimate_q10_bulk_hours`).
  2. **Python FastAPI Service & Mountable Router (`insight_bake/engine.py`, `router.py`, `server.py`)**:
     - Parametric `1..6` tier 3D scene graph supporting `ROUND` (`CylinderGeometry`), `SQUARE` (`BoxGeometry`), `HEART` (`ExtrudeHeartGeometry`), and `HEXAGON` (`6`-segment prism).
     - Exact gram-level BOM scaling, all **14 mandatory EU `Reg. (UE) n.º 1169/2011 Anexo II` allergens** + Portuguese counter signage (`DL n.º 26/2016`), Modulo-11 NIF validation, and Portugal AT IVA regimes (`13%` *Restauração* vs. `23%` *Take-Away*) with `ATCUD` 50% deposit preview.
     - **Arrhenius $Q_{10}$ Sourdough Fermentation & Baker's % Engine** (`/api/bake/fermentation`) with 3-factor Desired Dough Temperature (`DDT`) water calculation and bi-temporal ASAE HACCP lot traceability.
     - **Printable A4 ASAE Ficha Técnica** (`GET /api/bake/ficha-asae/print`) and **Live 24h Custom Cake Bridge** (`POST /api/bake/reserve-pastelaria` -> `InsightPastelaria :4029`).
  3. **Node.js / TypeScript SDK (`node_sdk/index.js`)**: `getBakeStatus`, `designCake3D`, `computeFermentation`, and `reserveCustomCakeInPastelaria`.
  4. **UX Engine 2.8 Studio & `<insight-bake>` Web Component (`ui_component/insight-bake.ts` & `/api/bake/studio`)**: Interactive `Three.js` WebGL viewport (with zero-dependency 2.5D isometric fallback and internal dowel X-ray toggle), roving `tabindex` modes, 1 Hero KPI + 3 secondary KPIs, and 4 async states (`WCAG 2.2 AA/AAA` & `DL n.º 82/2022`).

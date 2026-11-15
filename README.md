# SetMiddle Insight™ · Bake (`InsightBake` · `:4030 /api/bake`)

> **Company**: **SetMiddle** (`setmiddle.io` / `setmiddle.ai`)
> **Product Line**: **`SetMiddle Insight™`** (`SetMiddle Insight™ · Bake — Cake & Pastry 3D Studio`)
> **Internal Engine**: **`InsightCore`** (`insightCoreIO` + `insightCoreAI`)
> **Tagline**: Interactive `Three.js` 3D Multi-Tier Cake Configurator, `ComfyUI` ControlNet Photorealistic Studio Renderer, Gram-Exact Recipe BOM, EU Reg. 1169/2011 Allergen Label & Refrigerated Van Logistics

---

## 1. Why Hybrid `Three.js` 3D + `ComfyUI` ControlNet Beats Pure AI or Mini-Games
1. **Interactive `Three.js` 3D Parametric Builder (`/api/bake/studio` & `POST /api/bake/design`)**:
   - Configures `1 to 6` stacked tiers (`ROUND`, `SQUARE`, `HEART`, `HEXAGON`) with exact diameter/height (`cm`), sponge (*Pão de Ló*, *Red Velvet*, *Belga 70%*, *Amêndoa Sem Glúten*), filling (*Brigadeiro*, *Ovos Moles Conventuais*, *Lemon Curd*, *Praliné*), and frosting (*Swiss Meringue Buttercream*, *Fondant*, *Semi-Naked*).
   - **Prevents Structural Collapse**: Automatically rejects top-heavy inverted tiers (`INVERTED_UNSTABLE_TIER`) and computes the exact number and cut-height (`cm`) of internal polypropylene support dowels + center skewer.
2. **Zero-Hallucination `ComfyUI` ControlNet Photorealistic Studio Prompt**:
   - Locks the `Three.js` 3D Z-depth and Canny edges (`controlnet_depth_strength=0.88`) so `Flux.1-dev` / `SDXL` wraps photorealistic icing, Lambeth piping, and sugar flowers onto the **exact physical geometry** the baker can build.
3. **Gram-Exact Recipe Scaling, `MOD-FT-ASAE-DGAV-ACIP-v2.0` Vector A4 PDFs, `EU Reg. 1169/2011` Allergens & `AT` Deposit Invoicing**:
   - Calculates exact ingredient weights (`g`), all 14 statutory Annex II allergens + Horizontal A4 Counter Allergen Matrix PDF (`GET /api/bake/fichas-tecnicas/caderno-alergenios.pdf`), native Vector A4 Fichas Técnicas for both 3D Multi-Tier Cakes and Arrhenius $Q_{10}$ Sourdough batches (`GET/POST /api/bake/ficha-asae/pdf`), shared Economic Operator Modulo-11 NIF stamping (`GET/PUT /api/bake/estabelecimento`), baker labor hours, and the 50% `ATCUD` deposit invoice (`€`).
4. **Refrigerated Van Logistics, Multi-Locale SME Tax Exemption & `SetMiddle Insight™ · Fresco` (`:4029 /api/fresco`) Bridge (`v1.8.0`)**:
   - Computes required cake box dimensions (`cm`), `+2 °C to +5 °C` refrigerated transport target, `<= 0.35 g` cornering vibration limits, multi-jurisdiction SME tax exemption (`PT`, `ES`, `FR`, `DE`, `IT`, `GB`, `BR`, `US`, custom), and 24h custom-cake KDS + ASAE Ficha dispatch (`POST /api/bake/reserve-fresco` + legacy `/api/bake/reserve-pastelaria`).

# 📚 InsightBake Project Wiki (`v1.7.0`)

- **Workspace**: `PycharmProjects/InsightBake` (`:4030 /api/bake`)
- **System Architecture**: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Security & Statutory Policy**: [SECURITY.md](../SECURITY.md)

## Core Endpoints
| Method & Path | Description |
| :--- | :--- |
| `GET /health` & `GET /api/bake/status` | Service telemetry, 4 3D shapes, recipes, `MOD-FT-ASAE-DGAV-ACIP-v2.0` & 14 EU allergens |
| `GET / PUT /api/bake/estabelecimento` | Shared Official ASAE Establishment Profile (`Módulo-11` NIF, RJACSR/DGAV, HACCP Responsible) |
| `GET /api/bake/studio` | Interactive UX Engine 2.8 `Three.js` 3D Cake Studio + Cutaway Slice + X-Ray Dowels + Arrhenius Q10 |
| `POST /api/bake/design` / `POST /api/bake/execute` | Per-tier flavor 3D cake validation, BOM (`g`), EU-14 allergens, EU 1169 Art. 30 nutrition & melt countdown |
| `POST /api/bake/catering-timeline` & `/catering-cutting-guide/pdf` | Golden-Hour reverse setup timeline & Vector A4 Catering Cutting + Dowel Extraction Guide PDF |
| `POST /api/bake/stand-rentals` & `/{rental_id}/settle` | Reusable stand security deposit (`Caução` — `CIVA Art. 16.º n.º 6` `0% IVA` intact vs. `23% IVA` damage invoice) |
| `POST /api/bake/dietary-reformulate` | Structural-aware `GLUTEN_FREE_APC_20PPM` (`<=20 ppm`), `LACTOSE_FREE`, & `VEGAN_100PCT` reformulator |
| `POST /api/bake/solve-budget` | Reverse Guest-Count & Max-Budget 3D Cake Solver with allergen & ambient-temperature constraints |
| `POST /api/bake/tasting-box` | 4-Flavor Tasting Box (`Caixa de Prova`) issuing a 100% deposit-deductible voucher |
| `POST /api/bake/quotes` & `/quotes/{token}/approve` | Zero-PII Shareable Client Quote Portal with voucher credit, SHA-256 lock & automatic `:4029` KDS sync |
| `POST /api/bake/fleet-dispatch` & `/{id}/pod` | `InsightFleet` Cold-Chain + G-Force (`<=0.35g`) + AT `Guia de Transporte` (`DL 198/2012`) + `cas://` POD |
| `POST /api/bake/fermentation` | Arrhenius $Q_{10}$ sourdough fermentation kinetics, Baker's % & DDT water temperature |
| `POST /api/bake/deposit-checkout` & `/deposit-confirm` | SIBS `MB WAY` / `Multibanco` (`Modulo-97`) 50% deposit checkout & settlement receipt |
| `POST /api/bake/saft-pt-preview` & `/fiscal/saft-xml` | Locale-ready `SAF-T v1.04_01` SalesInvoice XML export (`PT`, `ES`, `FR`, `DE`, `IT`, `GB`, `BR`, `US`, custom — Standard VAT & `0%` SME Exemption with hard-cliff blocker) |
| `GET /api/bake/fiscal/locales` & `POST /fiscal/config` | Multi-jurisdiction fiscal profile catalog & active tax regime configuration (`STANDARD_VAT` vs. `EXEMPT_SMALL_BUSINESS`) |
| `POST /api/bake/fiscal/cliff-check` & `/fiscal/simulate-regime` | Pre-quote turnover cliff thermometer (`80%` / soft / hard cliff + EU SME cap) & Stay-Exempt vs. Voluntary VAT Opt-In CFO Simulator |
| `POST /api/bake/render-jobs` & `/{job_id}/cancel` | Non-blocking abortable `ComfyUI` ControlNet Z-depth render queue (`RULE-10`, `EU AI Act Art. 14`, `cas://`) |
| `POST /api/bake/search-recipes` | Allergen-safe & ambient-temperature constraint recipe ranker (Zero `ChromaDB` `RULE-16`) |
| `GET / POST /api/bake/ficha-asae/pdf` | Native Vector A4 Portrait PDF (`MOD-FT-ASAE-DGAV-ACIP-v2.0`) for 3D Cakes & Sourdough |
| `GET /api/bake/fichas-tecnicas/caderno-alergenios.pdf` | Native Vector A4 Landscape 14-Allergen Counter Matrix PDF (`Decreto-Lei n.º 26/2016`) |
| `POST /api/bake/reserve-pastelaria` | Dispatches 24h custom cake order + HTML/PDF ASAE Ficha into `InsightPastelaria` (`:4029`) |
| `POST /api/bake/scrub` | CNPD / GDPR (`Lei n.º 58/2019`) PII & Portuguese NIF scrubber |

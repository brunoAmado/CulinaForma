# 📚 InsightBake Project Wiki (`v1.4.0`)

- **Workspace**: `PycharmProjects/InsightBake` (`:4030 /api/bake`)
- **System Architecture**: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Security & Statutory Policy**: [SECURITY.md](../SECURITY.md)

## Core Endpoints
| Method & Path | Description |
| :--- | :--- |
| `GET /health` & `GET /api/bake/status` | Service telemetry, 4 3D shapes, recipes, `MOD-FT-ASAE-DGAV-ACIP-v2.0` & 14 EU allergens |
| `GET / PUT /api/bake/estabelecimento` | Shared Official ASAE Establishment Profile (`Módulo-11` NIF, RJACSR/DGAV, HACCP Responsible) |
| `GET /api/bake/studio` | Interactive UX Engine 2.8 `Three.js` 3D Cake Studio + Cutaway Slice + X-Ray Dowels + Arrhenius Q10 |
| `POST /api/bake/design` / `POST /api/bake/execute` | Per-tier flavor 3D cake validation, BOM (`g`), EU-14 allergens, EU 1169 Art. 30 nutrition & `ATCUD` |
| `POST /api/bake/fermentation` | Arrhenius $Q_{10}$ sourdough fermentation kinetics, Baker's % & DDT water temperature |
| `POST /api/bake/deposit-checkout` & `/deposit-confirm` | SIBS `MB WAY` / `Multibanco` (`Modulo-97`) 50% deposit checkout & settlement receipt |
| `POST /api/bake/saft-pt-preview` | Portugal AT `SAF-T (PT) v1.04_01` (`DL n.º 28/2019`) SalesInvoice XML export (`13%` / `23%` IVA) |
| `POST /api/bake/render-jobs` & `/{job_id}/cancel` | Non-blocking abortable `ComfyUI` ControlNet Z-depth render queue (`RULE-10`, `EU AI Act Art. 14`, `cas://`) |
| `POST /api/bake/search-recipes` | Allergen-safe & ambient-temperature constraint recipe ranker (Zero `ChromaDB` `RULE-16`) |
| `GET /api/bake/ficha-asae/print` | Printable A4 HTML ASAE Technical Data Sheet (`FT-ASAE-BAKE-*` & `FT-ASAE-FERM-*`) |
| `GET / POST /api/bake/ficha-asae/pdf` | Native Vector A4 Portrait PDF (`MOD-FT-ASAE-DGAV-ACIP-v2.0`) for 3D Cakes & Sourdough |
| `GET /api/bake/fichas-tecnicas/caderno-alergenios.pdf` | Native Vector A4 Landscape 14-Allergen Counter Matrix PDF (`Decreto-Lei n.º 26/2016`) |
| `POST /api/bake/reserve-pastelaria` | Dispatches 24h custom cake order + HTML/PDF ASAE Ficha into `InsightPastelaria` (`:4029`) |
| `POST /api/bake/scrub` | CNPD / GDPR (`Lei n.º 58/2019`) PII & Portuguese NIF scrubber |

# 📚 InsightBake Project Wiki (`v1.3.0`)

- **Workspace**: `PycharmProjects/InsightBake` (`:4030 /api/bake`)
- **System Architecture**: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Security & Statutory Policy**: [SECURITY.md](../SECURITY.md)

## Core Endpoints
| Method & Path | Description |
| :--- | :--- |
| `GET /health` & `GET /api/bake/status` | Service telemetry, 4 3D shapes, recipes, `MOD-FT-ASAE-DGAV-ACIP-v2.0` & 14 EU allergens |
| `GET / PUT /api/bake/estabelecimento` | Shared Official ASAE Establishment Profile (`Módulo-11` NIF, RJACSR/DGAV, HACCP Responsible) |
| `GET /api/bake/studio` | Interactive UX Engine 2.8 `Three.js` 3D Cake Studio + X-Ray Dowels + Arrhenius Q10 + Establishment Tabs |
| `POST /api/bake/design` / `POST /api/bake/execute` | 3D cake structural validation, BOM (`g`), EU-14 allergens, ControlNet spec & AT `ATCUD` pricing |
| `POST /api/bake/fermentation` | Arrhenius $Q_{10}$ sourdough fermentation kinetics, Baker's % & DDT water temperature |
| `GET /api/bake/ficha-asae/print` | Printable A4 HTML ASAE Technical Data Sheet (`FT-ASAE-BAKE-*` & `FT-ASAE-FERM-*`) |
| `GET / POST /api/bake/ficha-asae/pdf` | Native Vector A4 Portrait PDF (`MOD-FT-ASAE-DGAV-ACIP-v2.0`) for 3D Cakes & Sourdough |
| `GET /api/bake/fichas-tecnicas/caderno-alergenios.pdf` | Native Vector A4 Landscape 14-Allergen Counter Matrix PDF (`Decreto-Lei n.º 26/2016`) |
| `POST /api/bake/reserve-pastelaria` | Dispatches 24h custom cake order + HTML/PDF ASAE Ficha into `InsightPastelaria` (`:4029`) |
| `POST /api/bake/scrub` | CNPD / GDPR (`Lei n.º 58/2019`) PII & Portuguese NIF scrubber |

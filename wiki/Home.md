# 📚 InsightBake Project Wiki (`v1.2.0`)

- **Workspace**: `PycharmProjects/InsightBake` (`:4030 /api/bake`)
- **System Architecture**: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Security & Statutory Policy**: [SECURITY.md](../SECURITY.md)

## Core Endpoints
| Method & Path | Description |
| :--- | :--- |
| `GET /health` & `GET /api/bake/status` | Service telemetry, 4 3D shapes, recipes, and 14 EU allergens |
| `GET /api/bake/studio` | Interactive UX Engine 2.8 `Three.js` 3D Cake Studio + X-Ray Dowels + Arrhenius Q10 Lab |
| `POST /api/bake/design` / `POST /api/bake/execute` | 3D cake structural validation, BOM (`g`), EU-14 allergens, ControlNet spec & AT `ATCUD` pricing |
| `POST /api/bake/fermentation` | Arrhenius $Q_{10}$ sourdough fermentation kinetics, Baker's % & DDT water temperature |
| `GET /api/bake/ficha-asae/print` | Printable A4 ASAE Technical Data Sheet (`FT-ASAE-BAKE-*`) |
| `POST /api/bake/reserve-pastelaria` | Dispatches 24h custom cake order + ASAE Ficha into `InsightPastelaria` (`:4029`) |
| `POST /api/bake/scrub` | CNPD / GDPR (`Lei n.º 58/2019`) PII & Portuguese NIF scrubber |

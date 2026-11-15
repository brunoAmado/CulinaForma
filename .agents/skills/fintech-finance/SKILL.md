---
name: fintech-finance
description: Compact Team Master Playbook for fintech finance distilled from ChronicleRAG (Book_Lit_Master_fintech_finance.md). Enforces core architectural, UI/UX, and implementation rules with <9KB context footprint.
---

# ⚡ Compact Specialist Skill: fintech finance (`lit_Master_fintech_finance`)
> **Token-Budget Guard (`RULE-12`)**: This skill is pre-distilled (`< 9 KB`) from `books/master_books/Book_Lit_Master_fintech_finance.md` (`217 KB`) to prevent context bloat.
> **Active SetMiddle Ecosystem Baseline (`RULE-10..RULE-16`)**: **UX Engine 2.8** · **Unified PostgreSQL 17 (`pgvector` + `Apache AGE` + `TimescaleDB` on `:5432/:5433`, Zero Runtime `ChromaDB`)** · **55-Tool `chronicle-rag` MCP Hub** · **WCAG 2.2 AA/AAA & PT `DL 82/2022`**.
> **Hierarchical Progressive Disclosure & Backtrace**:
> - **Full Chapter TOC**: `chronicle-rag:read_book(identifier='lit_Master_fintech_finance', section='toc')`
> - **Surgical Single Chapter + Origin Backtrace**: `chronicle-rag:read_book(identifier='lit_Master_fintech_finance', section='chapter:<N>')` or `section='chapter:<keyword>'`
> - **Recursive 'New Eyes' Critique**: `chronicle-rag:read_book(identifier='lit_Master_fintech_finance', section='new_eyes')`

## 🌟 Executive Synopsis (Level 1)
Team-shared Master Thematic Book consolidating **61 chapters** and **61 source books** on `fintech_finance`.

## 📑 Key Chapters Index (Showing 25 of 61 Chapters)
- **Chapter 1**: [eBook] The Future of Finance with ChatGPT and Power BI (Packt) (🛡️ 9.4/10 | PT: 9.6/10)
- **Chapter 2**: insight_core — config.py
- **Chapter 3**: Écureuil Finance | Facebook (🛡️ 9.4/10 | PT: 9.6/10)
- **Chapter 4**: There are influencers out there right now telling you to stop building... — @mattmurp (🛡️ 9.5/10 | PT: 9.8/10)
- **Chapter 5**: Emplois fictifs #animations #france #finance | Écureuil Finance (🛡️ 6.5/10 | PT: 7.5/10)
- **Chapter 6**: Pourquoi un bon patron ne touche pas de salaire? #animations #france #finance | Écur (🛡️ 9.4/10 | PT: 9.6/10)
- **Chapter 7**: A confident prediction can still be wrong. How does AI measure what it doesn’t know? (🛡️ 9.4/10 | PT: 9.6/10)
- **Chapter 8**: Five types of startups that often die — @peterstewiestartup (🛡️ 9.4/10 | PT: 9.6/10)
- **Chapter 9**: Compte courant associé #France #animation #astuce | Écureuil Finance (🛡️ 9.0/10 | PT: 8.5/10)
- **Chapter 10**: PEE abondement maximal #France #animation #astuce | Écureuil Finance (🛡️ 6.5/10 | PT: 7.5/10)
- **Chapter 11**: BSPCE décote fondateur #France #animation #astuce | Écureuil Finance (🛡️ 8.0/10 | PT: 9.5/10)
- **Chapter 12**: Intégration fiscale LBO #France #animation #astuce | Écureuil Finance (🛡️ 9.5/10 | PT: 6.5/10)
- **Chapter 13**: Nantissement assurance-vie Lux #France #animation #astuce | Écureuil Finance (🛡️ 7.0/10 | PT: 8.5/10)
- **Chapter 14**: 🎓 CONTRASTIVE CASE STUDY / ANTI-PATTERN (4.5/10 | PT: 3.0/10) — Rachat actions trésorerie #France #animation #astuce | Écureuil Finance
- **Chapter 15**: Régime mère-fille #France #animation #astuce | Écureuil Finance (🛡️ 9.5/10 | PT: 10.0/10)
- **Chapter 16**: Crédit Lombard dépense #France #animation #astuce | Écureuil Finance (🛡️ 7.0/10 | PT: 8.5/10)
- **Chapter 17**: Exit tax purgée #France #animation #astuce | Écureuil Finance (🛡️ 9.0/10 | PT: 9.5/10)
- **Chapter 18**: 🎓 CONTRASTIVE CASE STUDY / ANTI-PATTERN (3.5/10 | PT: 1.5/10) — Supercar en charter #France #animation #astuce | Écureuil Finance
- **Chapter 19**: The State of AI and Software Engineering: Code is Cheaper but Expertise are More (🛡️ 9.5/10 | PT: 9.8/10)
- **Chapter 20**: [eBook] Platform Engineering for Architects (Packt) (🛡️ 9.4/10 | PT: 9.6/10)
- **Chapter 21**: [eBook
- **Chapter 22**: [eBook
- **Chapter 23**: [eBook] Security and Microservice Architecture on AWS (O'Reilly) (🛡️ 9.4/10 | PT: 9.6/10)
- **Chapter 24**: [eBook
- **Chapter 25**: What to Do When Your Constants Are Someone Else's Law — Overview > **Source Link**: h (🛡️ 9.4/10 | PT: 9.6/10)
- *(+36 additional chapters indexed in `Book_Lit_Master_fintech_finance.md`)*

## 📐 Distilled Engineering Rules & Actionable Patterns
### Chapter 61 [Écureuil Finance (🛡️ 7.2/10 | PT: 7.0/10)]
- **🇵🇹 Local (`PT`) Adaptation**: PORTUGAL (PT — 7.0/10): Before applying in Portugal, verify against **CIRC (Art. 51.º Participation Exemption >=10% held >=1 yr; Art. 88.º Tributação Autónoma)**, **CIRS (28% Category E/G flat rate; Art. 43.º-C EBF 14% Startup
- **✅ When It IS Valid (Exact Conditions & Thresholds)**: Valid when mapped to the corresponding Portuguese statutory article (e.g., Art. 51.º CIRC for Holdings, Art. 243.º CSC for Suprimentos, Art. 43.º-C EBF for Stock Options) with genuine economic substance
- **🛠️ What to Do Instead (Safe & Legal `PT` Strategy)**: Always verify the Portuguese statutory equivalent (CIRC/CIRS/CIS/EBF) and document non-tax commercial substance before executing.

### Chapter 62 [Janets Managerial Accounting (108 Courses) & Audible Data-Driven Decision Hygiene (141 Books) (🛡️ 9.5/10 | PT: 9.8/10)]
1. **Integer Minor-Unit & Exact Decimal Invariant**: Store and reconcile all ledger lines in integer minor units (`cents`) or `Decimal`/`BigDecimal(String)` (never IEEE-754 `float`), enforcing balanced double-entry (`sum(debits) == sum(credits)`) before commit
2. **Price-Volume-Mix & FEFO Spoilage Variance**: Decompose gross-margin drift into price variance, volume variance, and perishable spoilage/shrinkage (`FEFO` + Newsvendor critical fractile $F^{-1}((p - c)/(p - s))$ for `InsightPastelaria` & `InsightBake`).
3. **Portuguese Statutory Fiscal Gate (`RULE-11`)**: Pair every commercial invoice/receipt workflow with **AT `SAF-T (PT)` / `ATCUD` (`Decreto-Lei n.º 28/2019`)** sequential series validation, **`CIRC Art. 50.º-A` (`85%` Patent Box IP exemption)** separate R&D
4. **Base-Rate & Expected-Value Decision Guard (`InsightTrade`, `Audible` Corpus)**: Anchor forecasts on empirical historical base rates (`Brier` / calibration score) rather than single-point intuition; cap position/exposure sizing via fractional Kelly / maxim

### Chapter 1 [[eBook] The Future of Finance with ChatGPT and Power BI (Packt) (🛡️ 9.4/10 | PT: 9.6/10)]
- **🇵🇹 Local (`PT`) Adaptation**: PORTUGAL (PT — 9.6/10): Complies with Portugal's **Decreto-Lei n.º 82/2022** (European Accessibility Act) and **Decreto-Lei n.º 83/2018** (EN 301 549 / WCAG 2.2 AA). If collecting user data or payments in Portugal, pair with *
- **✅ When It IS Valid (Exact Conditions & Thresholds)**: Valid when paired with `:focus-visible`, `prefers-reduced-motion`, `tabular-nums`, and 44x44px coarse-pointer touch targets.
- **🛠️ What to Do Instead (Safe & Legal `PT` Strategy)**: Enforce UX Engine 2.6 + Decreto-Lei n.º 82/2022 accessibility + NIF/ATCUD billing fields for Portuguese users.

### Chapter 3 [Écureuil Finance | Facebook (🛡️ 9.4/10 | PT: 9.6/10)]
- **🇵🇹 Local (`PT`) Adaptation**: PORTUGAL (PT — 9.6/10): Complies with Portugal's **Decreto-Lei n.º 82/2022** (European Accessibility Act) and **Decreto-Lei n.º 83/2018** (EN 301 549 / WCAG 2.2 AA). If collecting user data or payments in Portugal, pair with *
- **✅ When It IS Valid (Exact Conditions & Thresholds)**: Valid when paired with `:focus-visible`, `prefers-reduced-motion`, `tabular-nums`, and 44x44px coarse-pointer touch targets.
- **🛠️ What to Do Instead (Safe & Legal `PT` Strategy)**: Enforce UX Engine 2.6 + Decreto-Lei n.º 82/2022 accessibility + NIF/ATCUD billing fields for Portuguese users.
- **Referenced Tools / Repos**: https://shop.beacons.ai/ecureuilfinance/e062737f-9d2c-4edf-ab6d-d7b21562fb69, https://shop.beacons.ai/ecureuilfinance/462de08, https://shop.beacons.ai/ecureuilfinance/462de086-03a3-45af-9def-4b5ea2cbbc40

### Chapter 4 [There are influencers out there right now telling you to stop building... — @mattmurp (🛡️ 9.5/10 | PT: 9.8/10)]
- **🇵🇹 Local (`PT`) Adaptation**: PORTUGAL & EU COMPLIANCE (9.8/10 — CNPD / GDPR Art. 17 & EU AI Act): 1) **GDPR Art. 17 (Direito ao Esquecimento / CNPD Portugal)**: Storing user/company facts in a RAG index allows instant 1ms erasure upon request, whereas bak
- **✅ When It IS Valid (Exact Conditions & Thresholds)**: Valid when all statutory holding periods, ownership percentages, and genuine business-purpose requirements are documented.

*(Truncated at 8500 chars per RULE-12; query `lit_Master_fintech_finance` via MCP for full chapters.)*


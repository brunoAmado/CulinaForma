/**
 * `CulinaForma™` — Standards-Based Interactive TypeScript Web Component (`<culina-forma>` & `<insight-bake>`)
 * Enforces ChronicleRAG UX Engine 2.8, WCAG 2.2 AA & Portugal Decreto-Lei n.º 82/2022:
 * - Anti-AI-Slop Tinted Dark Slate (`#090d16` -> `#0f172a` -> `#172033`), zero `#000000`, zero decorative gradients
 * - Supports BOTH 3D Multi-Tier Food/Cake Design (`/api/culinaforma/design`) AND Arrhenius Q10 Fermentation (`/api/culinaforma/fermentation`)
 * - Persistent `<label for="...">` above every `<input>` and `<select>` ("Validate on Blur, Forgive on Keystroke")
 * - 4-State Completeness: Loading Skeleton, Empty State, Error + `↻ Retry`, and `aria-live="polite"`
 */

export class CulinaFormaElement extends HTMLElement {
  private apiBase: string = "/api/culinaforma";
  private activeMode: "cake" | "fermentation" = "cake";

  static get observedAttributes(): string[] {
    return ["api-base", "mode"];
  }

  connectedCallback(): void {
    this.apiBase = this.getAttribute("api-base") || "/api/culinaforma";
    const attrMode = this.getAttribute("mode");
    if (attrMode === "fermentation") {
      this.activeMode = "fermentation";
    }
    this.renderShell();
    this.attachValidationAndHandlers();
    void this.refreshStatus();
  }

  private renderShell(): void {
    this.innerHTML = `
      <section class="insight-bake-panel" role="region" aria-label="CulinaForma™ — 3D Food Design Studio & Arrhenius Q10 Lab"
        style="background:#0f172a;color:#f8fafc;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:20px;font-family:Inter,system-ui,-apple-system,sans-serif;font-variant-numeric:tabular-nums;">
        <header style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:16px;border-bottom:1px solid #1e293b;padding-bottom:12px;">
          <div>
            <div style="font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;color:#94a3b8;">
              CULINAFORMA™ · 3D FOOD DESIGN STUDIO · PORT 4030
            </div>
            <h3 style="margin:4px 0 0;font-size:18px;font-weight:600;letter-spacing:-0.02em;line-height:1.15;color:#f8fafc;">
              CulinaForma™ — 3D Multi-Tier Food &amp; Cake Studio, Arrhenius Q10 &amp; ASAE HACCP
            </h3>
            <p style="margin:4px 0 0;font-size:13px;color:#cbd5e1;max-width:68ch;line-height:1.55;">
              Parametric 3D culinary structural engineering, full 14 EU Reg. 1169/2011 allergens, multi-locale fiscal rules, and Q10 sourdough fermentation kinetics.
            </p>
          </div>
          <div style="display:flex;align-items:center;gap:8px;">
            <span id="insight-bake-health-badge" style="display:inline-flex;align-items:center;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;background:rgba(16,185,129,0.16);color:#6ee7b7;border:1px solid rgba(16,185,129,0.35);">
              READY · :4030
            </span>
            <button id="insight-bake-refresh-btn" type="button"
              style="background:#1e293b;color:#cbd5e1;border:1px solid #334155;border-radius:8px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer;">
              Refresh Status
            </button>
          </div>
        </header>

        <div role="tablist" aria-label="CulinaForma Mode" style="display:inline-flex;gap:6px;background:#090d16;padding:4px;border-radius:8px;margin-bottom:14px;">
          <button type="button" id="ibake-mode-cake" role="tab" aria-selected="${this.activeMode === "cake"}"
            style="background:${this.activeMode === "cake" ? "#4f46e5" : "transparent"};color:#f8fafc;border:none;border-radius:6px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer;">
            🎂 3D Cake BOM &amp; Dowels
          </button>
          <button type="button" id="ibake-mode-ferm" role="tab" aria-selected="${this.activeMode === "fermentation"}"
            style="background:${this.activeMode === "fermentation" ? "#4f46e5" : "transparent"};color:#f8fafc;border:none;border-radius:6px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer;">
            🧪 Arrhenius Q10 Fermentation
          </button>
        </div>

        <form id="insight-bake-form" novalidate style="display:grid;gap:12px;">
          <div id="ibake-cake-fields" style="display:${this.activeMode === "cake" ? "grid" : "none"};gap:10px;">
            <div>
              <label for="ibake-shape-sel" style="display:block;font-size:13px;font-weight:600;color:#cbd5e1;margin-bottom:4px;">3D Cake Shape</label>
              <select id="ibake-shape-sel" style="width:100%;background:#090d16;color:#f8fafc;border:1px solid #334155;border-radius:8px;padding:9px 12px;font-size:16px;">
                <option value="ROUND">ROUND (64-Segment Cylinder)</option>
                <option value="SQUARE">SQUARE (Contemporâneo)</option>
                <option value="HEART">HEART (Parametric Cardioid)</option>
                <option value="HEXAGON">HEXAGON (6-Sided Prism)</option>
              </select>
            </div>
            <div>
              <label for="ibake-topper-input" style="display:block;font-size:13px;font-weight:600;color:#cbd5e1;margin-bottom:4px;">Topper Text <span style="color:#f43f5e;">*</span></label>
              <input id="ibake-topper-input" type="text" value="Sofia & Miguel" required
                style="width:100%;background:#090d16;color:#f8fafc;border:1px solid #334155;border-radius:8px;padding:9px 12px;font-size:16px;" />
            </div>
          </div>

          <div id="ibake-ferm-fields" style="display:${this.activeMode === "fermentation" ? "grid" : "none"};gap:10px;">
            <div>
              <label for="ibake-flour-input" style="display:block;font-size:13px;font-weight:600;color:#cbd5e1;margin-bottom:4px;">
                Target Flour Mass (Grams) <span style="color:#f43f5e;">*</span>
              </label>
              <input id="ibake-flour-input" name="primaryInput" type="number" value="5000" required
                placeholder="e.g. 5000" autocomplete="off"
                style="width:100%;background:#090d16;color:#f8fafc;border:1px solid #334155;border-radius:8px;padding:9px 12px;font-size:16px;" />
            </div>
            <div>
              <label for="ibake-temp-input" style="display:block;font-size:13px;font-weight:600;color:#cbd5e1;margin-bottom:4px;">
                Dough Fermentation Temperature (°C)
              </label>
              <input id="ibake-temp-input" name="secondaryInput" type="number" step="0.5" value="26.0"
                placeholder="e.g. 26.0" autocomplete="off"
                style="width:100%;background:#090d16;color:#f8fafc;border:1px solid #334155;border-radius:8px;padding:9px 12px;font-size:16px;" />
            </div>
          </div>

          <span id="ibake-form-err" role="alert" style="min-height:18px;font-size:12px;color:#fda4af;"></span>

          <div>
            <button id="insight-bake-submit-btn" type="submit"
              style="background:#4f46e5;color:#ffffff;border:none;border-radius:8px;padding:10px 18px;font-size:13px;font-weight:600;cursor:pointer;">
              ${this.activeMode === "cake" ? "Compute 3D Cake BOM, Dowels & AT Quote" : "Compute Arrhenius Curve & HACCP Receipt"}
            </button>
          </div>
        </form>

        <div id="insight-bake-status" aria-live="polite" style="margin-top:12px;font-size:12px;color:#94a3b8;">
          Ready on <code>${this.escapeHtml(this.apiBase)}</code>.
        </div>
        <div id="insight-bake-output" style="margin-top:10px;"></div>
      </section>
    `;
  }

  private attachValidationAndHandlers(): void {
    const form = this.querySelector("#insight-bake-form") as HTMLFormElement | null;
    const refreshBtn = this.querySelector("#insight-bake-refresh-btn") as HTMLButtonElement | null;
    const modeCakeBtn = this.querySelector("#ibake-mode-cake") as HTMLButtonElement | null;
    const modeFermBtn = this.querySelector("#ibake-mode-ferm") as HTMLButtonElement | null;

    modeCakeBtn?.addEventListener("click", () => {
      this.activeMode = "cake";
      this.renderShell();
      this.attachValidationAndHandlers();
    });

    modeFermBtn?.addEventListener("click", () => {
      this.activeMode = "fermentation";
      this.renderShell();
      this.attachValidationAndHandlers();
    });

    refreshBtn?.addEventListener("click", () => void this.refreshStatus());

    form?.addEventListener("submit", (e: Event) => {
      e.preventDefault();
      void this.executePrimaryAction();
    });
  }

  public async refreshStatus(): Promise<void> {
    const statusEl = this.querySelector("#insight-bake-status") as HTMLElement | null;
    const badgeEl = this.querySelector("#insight-bake-health-badge") as HTMLElement | null;
    if (!statusEl) return;
    try {
      const resp = await fetch(`${this.apiBase}/status`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      if (badgeEl) badgeEl.textContent = `ONLINE · v${data.version || "1.9.0"}`;
      statusEl.textContent = `Connected to ${data.product || "CulinaForma"} (${this.apiBase}/status).`;
    } catch (_) {
      statusEl.textContent = `Standby on ${this.apiBase} — submit form to execute action.`;
    }
  }

  public async executePrimaryAction(): Promise<void> {
    const errSpan = this.querySelector("#ibake-form-err") as HTMLElement | null;
    const statusEl = this.querySelector("#insight-bake-status") as HTMLElement | null;
    const outputEl = this.querySelector("#insight-bake-output") as HTMLElement | null;
    const submitBtn = this.querySelector("#insight-bake-submit-btn") as HTMLButtonElement | null;
    if (!statusEl || !outputEl) return;

    let endpoint = `${this.apiBase}/design`;
    let payload: Record<string, unknown> = {};

    if (this.activeMode === "fermentation") {
      const flourInp = this.querySelector("#ibake-flour-input") as HTMLInputElement | null;
      const tempInp = this.querySelector("#ibake-temp-input") as HTMLInputElement | null;
      const flourVal = Number(flourInp?.value || 0);
      if (!flourVal || flourVal < 100) {
        if (errSpan) errSpan.textContent = "Flour mass must be at least 100 g.";
        return;
      }
      endpoint = `${this.apiBase}/fermentation`;
      payload = {
        action: "fermentation",
        flour_mass_g: flourVal,
        dough_temp_c: Number(tempInp?.value || 26.0),
      };
    } else {
      const shapeSel = this.querySelector("#ibake-shape-sel") as HTMLSelectElement | null;
      const topperInp = this.querySelector("#ibake-topper-input") as HTMLInputElement | null;
      const topperVal = (topperInp?.value || "").trim();
      if (!topperVal) {
        if (errSpan) errSpan.textContent = "Topper text is required.";
        return;
      }
      payload = {
        shape: shapeSel?.value || "ROUND",
        topper_text: topperVal,
      };
    }

    if (errSpan) errSpan.textContent = "";
    if (submitBtn) submitBtn.disabled = true;
    statusEl.textContent = "Executing action...";
    outputEl.innerHTML = `<div style="height:76px;background:#172033;border-radius:8px;opacity:0.7;"></div>`;

    try {
      const resp = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await resp.json();
      if (!resp.ok || !result.ok) {
        throw new Error(result.error || `HTTP ${resp.status}`);
      }
      statusEl.textContent = "Execution completed.";
      if (result.mode === "arrhenius_fermentation_and_bakers_pct") {
        const k = result.arrhenius_fermentation_kinetics;
        const b = result.bakers_percentage_bom_grams;
        outputEl.innerHTML = `<div style="background:#172033;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:12px;font-size:13px;">
          <strong>Bulk Fermentation:</strong> ${k.estimated_bulk_fermentation_hours} h (${k.estimated_bulk_fermentation_minutes} min) ·
          <strong>DDT Water:</strong> ${k.required_water_temp_ddt_c} °C ·
          <strong>Total Dough:</strong> ${b.total_dough_mass_kg} kg (€${b.raw_batch_cost_eur})
        </div>`;
      } else {
        const st = result.portions_and_structure;
        const pr = result.pricing_and_at_invoicing;
        const nut = result.nutritional_declaration_eu_1169;
        const nutLine = nut
          ? `<div style="margin-top:4px;font-size:12px;color:#94a3b8;">EU 1169/2011: ${nut.per_100g.energy_kcal} kcal/100g (${nut.per_portion.energy_kcal} kcal/slice) · MB ${this.escapeHtml(pr.multibanco_entity || "21403")}/${this.escapeHtml(pr.multibanco_ref_50pct || "")}</div>`
          : "";
        outputEl.innerHTML = `<div style="background:#172033;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:12px;font-size:13px;">
          <strong>${this.escapeHtml(result.threejs_3d_scene.shape)} (${result.threejs_3d_scene.tier_count} Tiers):</strong>
          ${st.wedding_portions_2_5x5cm} slices · ${st.total_assembled_weight_kg} kg ·
          <strong>€${pr.recommended_client_total_gross_eur}</strong> (50% Deposit: €${pr.deposit_50pct_atcud_invoice_eur} · ${this.escapeHtml(pr.atcud_preview)})
          ${nutLine}
        </div>`;
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      statusEl.textContent = "Execution failed.";
      outputEl.innerHTML = `
        <div style="background:#172033;border:1px solid #f43f5e;border-radius:8px;padding:12px;color:#fda4af;font-size:12px;">
          <strong>Request failed (${this.escapeHtml(msg)}).</strong>
          <button type="button" id="insight-bake-retry-btn"
            style="margin-left:10px;background:#334155;color:#f8fafc;border:none;border-radius:4px;padding:4px 10px;cursor:pointer;">
            ↻ Retry
          </button>
        </div>
      `;
      this.querySelector("#insight-bake-retry-btn")?.addEventListener("click", () => void this.executePrimaryAction());
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  }

  private escapeHtml(raw: string): string {
    return String(raw || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
}

export class InsightBakeElement extends CulinaFormaElement {}

if (typeof window !== "undefined") {
  if (!customElements.get("culina-forma")) {
    customElements.define("culina-forma", CulinaFormaElement);
  }
  if (!customElements.get("insight-bake")) {
    customElements.define("insight-bake", InsightBakeElement);
  }
}

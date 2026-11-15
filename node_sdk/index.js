/**
 * SetMiddle Insight™ · Bake — Node.js / TypeScript SDK (`:4030 /api/bake`)
 * Covers 3D Multi-Tier Cake Engineering, Arrhenius Q10 Fermentation, ASAE Fichas & InsightPastelaria (:4029) Handoff.
 */

export async function getBakeStatus(baseUrl = "http://127.0.0.1:4030") {
  const res = await fetch(`${baseUrl}/api/bake/status`);
  if (!res.ok) throw new Error(`InsightBake status HTTP ${res.status}`);
  return res.json();
}

export async function designCake3D(baseUrl = "http://127.0.0.1:4030", payload = {}) {
  const res = await fetch(`${baseUrl}/api/bake/design`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function computeFermentation(
  baseUrl = "http://127.0.0.1:4030",
  { flour_mass_g = 5000, dough_temp_c = 26.0, hydration_pct = 72.0, starter_pct = 20.0 } = {}
) {
  const res = await fetch(`${baseUrl}/api/bake/fermentation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: "fermentation",
      flour_mass_g,
      dough_temp_c,
      hydration_pct,
      starter_pct,
    }),
  });
  return res.json();
}

export async function reserveCustomCakeInPastelaria(baseUrl = "http://127.0.0.1:4030", payload = {}) {
  const res = await fetch(`${baseUrl}/api/bake/reserve-pastelaria`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function createDepositCheckout(baseUrl = "http://127.0.0.1:4030", payload = {}) {
  const res = await fetch(`${baseUrl}/api/bake/deposit-checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function confirmDepositPayment(baseUrl = "http://127.0.0.1:4030", { payment_id, transaction_ref = "SIBS-ACK-OK" } = {}) {
  const res = await fetch(`${baseUrl}/api/bake/deposit-confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ payment_id, transaction_ref }),
  });
  return res.json();
}

export async function exportSaftPtPreview(baseUrl = "http://127.0.0.1:4030", payload = {}) {
  const res = await fetch(`${baseUrl}/api/bake/saft-pt-preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function submitAsyncComfyRenderJob(baseUrl = "http://127.0.0.1:4030", payload = {}) {
  const res = await fetch(`${baseUrl}/api/bake/render-jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function searchSafeCakeRecipes(baseUrl = "http://127.0.0.1:4030", payload = {}) {
  const res = await fetch(`${baseUrl}/api/bake/search-recipes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

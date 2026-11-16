/**
 * CulinaForma™ — Node.js / TypeScript SDK (`:4030 /api/culinaforma`, backward-compatible `/api/bake`)
 * Covers 3D Multi-Tier Food & Cake Engineering, Arrhenius Q10 Fermentation, ASAE Fichas & InsightFresco (:4029) Handoff.
 */

export async function getCulinaFormaStatus(baseUrl = "http://127.0.0.1:4030", apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/status`);
  if (!res.ok) throw new Error(`CulinaForma status HTTP ${res.status}`);
  return res.json();
}

export const getBakeStatus = getCulinaFormaStatus;

export async function designCake3D(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/design`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export const designFood3D = designCake3D;

export async function computeFermentation(
  baseUrl = "http://127.0.0.1:4030",
  { flour_mass_g = 5000, dough_temp_c = 26.0, hydration_pct = 72.0, starter_pct = 20.0 } = {},
  apiPrefix = "/api/culinaforma"
) {
  const res = await fetch(`${baseUrl}${apiPrefix}/fermentation`, {
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

export async function reserveCustomCakeInFresco(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/reserve-fresco`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function reserveCustomCakeInPastelaria(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/reserve-pastelaria`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function createDepositCheckout(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/deposit-checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function confirmDepositPayment(baseUrl = "http://127.0.0.1:4030", { payment_id, transaction_ref = "SIBS-ACK-OK" } = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/deposit-confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ payment_id, transaction_ref }),
  });
  return res.json();
}

export async function exportSaftPtPreview(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/saft-pt-preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function submitAsyncComfyRenderJob(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/render-jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function searchSafeCakeRecipes(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/search-recipes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function solveCakeByGuestsAndBudget(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/solve-budget`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function createTastingBoxOrder(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/tasting-box`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function createShareableClientQuote(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/quotes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function dispatchRefrigeratedFleet(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/fleet-dispatch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function buildCateringCuttingTimeline(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/catering-timeline`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function createStandRentalDeposit(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/stand-rentals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function reformulateDietarySafeCake(baseUrl = "http://127.0.0.1:4030", payload = {}, apiPrefix = "/api/culinaforma") {
  const res = await fetch(`${baseUrl}${apiPrefix}/dietary-reformulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

"""
FastAPI `APIRouter` Plugin for `SetMiddle Insight™ · Bake` (`insight_bake.router`).
Can be mounted standalone (`:4030`) or inside `ChronicleRAG` (`:8765`).
Enforces UX Engine 2.8, WCAG 2.2 AA/AAA & Portugal Decreto-Lei n.º 82/2022.
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Body, FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response

from insight_bake.engine import (
    InsightBakeEngine,
    compute_arrhenius_fermentation_and_bakers_pct,
    render_cake_asae_ficha_html,
)


INTERACTIVE_3D_CAKE_STUDIO_HTML = """<!DOCTYPE html>
<html lang="pt-PT" class="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#090d16">
<title>SetMiddle Insight™ · Bake — Estúdio 3D Cake Design, Fermentação Arrhenius &amp; Ficha ASAE</title>
<style>
  :root {
    --canvas: #090d16;
    --surface: #0f172a;
    --card: #172033;
    --hover: #1e293b;
    --border: rgba(255, 255, 255, 0.08);
    --accent: #4f46e5;
    --accent-hover: #4338ca;
    --focus: #818cf8;
  }
  * { box-sizing: border-box; }
  body {
    background: var(--canvas);
    color: #f8fafc;
    font-family: Inter, system-ui, -apple-system, sans-serif;
    margin: 0;
    padding: 0 0 48px;
    font-variant-numeric: tabular-nums;
  }
  .skip-link {
    position: absolute;
    left: -9999px;
    top: 8px;
    z-index: 1000;
    background: var(--accent);
    color: #fff;
    padding: 8px 14px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
  }
  .skip-link:focus { left: 12px; }
  :focus-visible { outline: 2px solid var(--focus) !important; outline-offset: 2px !important; }
  .sr-only {
    position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
    overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
  }
  header.topbar {
    position: sticky; top: 0; z-index: 40;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
  }
  .topbar-inner {
    max-width: 1280px; margin: 0 auto;
    display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;
  }
  .container { max-width: 1280px; margin: 0 auto; padding: 20px; }
  .hero-kpis {
    display: grid; grid-template-columns: 2fr repeat(3, 1fr); gap: 12px; margin-bottom: 18px;
  }
  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
  }
  .tile {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px; /* Concentric: 16px outer - 8px gap = 8px inner */
    padding: 12px;
  }
  .grid-studio {
    display: grid; grid-template-columns: 380px 1fr; gap: 18px; align-items: start;
  }
  h1 { font-size: 20px; margin: 4px 0 0; letter-spacing: -0.02em; }
  h2 { font-size: 14px; margin: 0 0 12px; color: #c7d2fe; text-transform: uppercase; letter-spacing: 0.05em; }
  label { display: block; font-size: 12px; color: #cbd5e1; margin: 10px 0 4px; font-weight: 600; }
  select, input[type="text"], input[type="number"] {
    width: 100%; background: var(--canvas); color: #f8fafc;
    border: 1px solid #334155; border-radius: 8px; padding: 9px 11px; font-size: 16px;
  }
  button {
    font-family: inherit; font-variant-numeric: tabular-nums;
    border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 13px;
    padding: 9px 14px; border: 1px solid transparent;
  }
  button.primary { background: var(--accent); color: #fff; width: 100%; margin-top: 14px; font-size: 14px; padding: 11px 16px; }
  button.primary:hover { background: var(--accent-hover); }
  button.secondary { background: var(--card); color: #e2e8f0; border-color: #334155; }
  button.secondary:hover { background: var(--hover); }
  button:disabled { opacity: 0.55; cursor: not-allowed; }
  .tablist { display: inline-flex; gap: 6px; background: var(--canvas); padding: 4px; border-radius: 10px; border: 1px solid var(--border); }
  .tab-btn { background: transparent; color: #94a3b8; padding: 7px 12px; font-size: 12px; }
  .tab-btn[aria-selected="true"] { background: var(--accent); color: #fff; }
  #viewport-3d {
    width: 100%; height: 350px; background: var(--canvas);
    border: 1px solid var(--border); border-radius: 10px;
    position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center;
  }
  .tier-row { display: grid; grid-template-columns: 1fr 1fr auto; gap: 8px; align-items: end; margin-bottom: 8px; }
  .badge { display: inline-flex; align-items: center; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; }
  .badge-allergen { background: rgba(244, 63, 94, 0.15); color: #fecdd3; border: 1px solid rgba(244, 63, 94, 0.35); margin: 2px; }
  .skeleton { height: 72px; background: var(--card); border-radius: 8px; opacity: 0.65; }
  table.bom-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }
  table.bom-table th, table.bom-table td { padding: 7px 8px; border-bottom: 1px solid rgba(255,255,255,0.06); text-align: left; }
  table.bom-table th { color: #94a3b8; font-weight: 600; }
  .hidden { display: none !important; }
  .drawer-toggle { display: none; }
  @media (max-width: 900px) {
    .hero-kpis { grid-template-columns: 1fr 1fr; }
    .grid-studio { grid-template-columns: 1fr; }
  }
  @media (max-width: 767px) {
    .drawer-toggle { display: inline-flex; }
    .tablist {
      display: none; position: fixed; top: 62px; left: 12px; right: 12px; z-index: 50;
      flex-direction: column; background: var(--surface); padding: 10px; box-shadow: 0 16px 32px rgba(0,0,0,0.55);
    }
    .tablist.open { display: flex; }
    table.mobile-card-table thead { display: none; }
    table.mobile-card-table tbody tr {
      display: block; background: var(--card); border: 1px solid var(--border);
      border-radius: 8px; padding: 8px 10px; margin-bottom: 8px;
    }
    table.mobile-card-table tbody td { display: flex; justify-content: space-between; border: none; padding: 3px 0; }
  }
  @media (pointer: coarse) {
    button, select, input { min-height: 44px; }
  }
</style>
</head>
<body>
<a href="#main-content" class="skip-link">Saltar para o conteúdo principal</a>
<div id="sr-announcer" class="sr-only" aria-live="polite"></div>

<header class="topbar" role="banner">
  <div class="topbar-inner">
    <div>
      <span style="font-size:11px;color:#a5b4fc;font-weight:600;letter-spacing:0.05em;">SETMIDDLE INSIGHT™ · BAKE · PORTA 4030</span>
      <h1>🎂 SetMiddle Insight™ · Bake — Estúdio 3D Cake Design, Fermentação Arrhenius &amp; ASAE</h1>
    </div>
    <button type="button" class="secondary drawer-toggle" id="mobile-menu-btn" aria-expanded="false" aria-controls="main-tablist" onclick="toggleMobileDrawer()">
      ☰ Modos
    </button>
    <div id="main-tablist" class="tablist" role="tablist" aria-label="Modos do Estúdio InsightBake" onkeydown="onTabKeydown(event)">
      <button id="tab-cake" class="tab-btn" role="tab" aria-selected="true" aria-controls="view-cake" tabindex="0" onclick="switchMode('cake')">
        🎂 Estúdio 3D Multi-Andar
      </button>
      <button id="tab-ferment" class="tab-btn" role="tab" aria-selected="false" aria-controls="view-ferment" tabindex="-1" onclick="switchMode('ferment')">
        🧪 Fermentação Arrhenius (Q10)
      </button>
    </div>
  </div>
</header>

<main id="main-content" class="container">
  <!-- UX Engine 2.8: 1 Primary Hero Metric + 3 Compact Secondary Metrics -->
  <section class="hero-kpis" aria-label="Indicadores Principais do Projeto">
    <div class="panel" style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
      <div>
        <div style="font-size:11px;color:#a5b4fc;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">Orçamento Total c/ IVA &amp; Sinal 50% ATCUD</div>
        <div id="hero-price" style="font-size:28px;font-weight:700;color:#f8fafc;margin-top:4px;">€248.50</div>
        <div id="hero-atcud" style="font-size:12px;color:#94a3b8;margin-top:2px;">Sinal 50%: €124.25 · IVA 13%</div>
      </div>
      <span id="stability-pill" class="badge" style="background:rgba(16,185,129,0.16);color:#6ee7b7;border:1px solid rgba(16,185,129,0.35);">Estável (Estacas OK)</span>
    </div>
    <div class="panel">
      <div style="font-size:11px;color:#94a3b8;">Fatias Casamento / Festa</div>
      <div id="kpi-portions" style="font-size:20px;font-weight:700;color:#e2e8f0;margin-top:4px;">105 / 58</div>
      <div style="font-size:11px;color:#64748b;">2.5×5 cm vs 5×5 cm</div>
    </div>
    <div class="panel">
      <div style="font-size:11px;color:#94a3b8;">Peso Total Montado</div>
      <div id="kpi-weight" style="font-size:20px;font-weight:700;color:#e2e8f0;margin-top:4px;">9.40 kg</div>
      <div id="kpi-box" style="font-size:11px;color:#64748b;">Caixa Frio +2..+5 °C</div>
    </div>
    <div class="panel">
      <div style="font-size:11px;color:#94a3b8;">Alergénios UE 1169/2011</div>
      <div id="kpi-allergen-count" style="font-size:20px;font-weight:700;color:#fda4af;margin-top:4px;">4 Anexo II</div>
      <div style="font-size:11px;color:#64748b;">Dístico ASAE DL 26/2016</div>
    </div>
  </section>

  <!-- VIEW 1: 3D MULTI-TIER CAKE CONFIGURATOR -->
  <div id="view-cake" role="tabpanel" aria-labelledby="tab-cake" class="grid-studio">
    <section class="panel" aria-label="Configurador Paramétrico de Andares e Sabores">
      <h2>1. Geometria 3D (1 a 6 Andares) &amp; Receita</h2>

      <label for="shape-sel">Formato Geométrico 3D</label>
      <select id="shape-sel" onchange="recalcCake()">
        <option value="ROUND">Redondo Clássico (Cylinder 64-Seg)</option>
        <option value="SQUARE">Quadrado Contemporâneo (Box)</option>
        <option value="HEART">Coração Romântico (Parametric Heart)</option>
        <option value="HEXAGON">Hexagonal Geométrico (6 Faces)</option>
      </select>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px;">
        <span style="font-size:12px;font-weight:600;color:#cbd5e1;">Andares Empilhados (Base → Topo)</span>
        <div style="display:flex;gap:6px;">
          <button type="button" class="secondary" style="padding:5px 10px;font-size:12px;" onclick="addTier()">+ Andar</button>
          <button type="button" class="secondary" style="padding:5px 10px;font-size:12px;" onclick="removeTier()">− Andar</button>
        </div>
      </div>
      <div id="tiers-editor" style="margin-top:8px;"></div>

      <label for="sponge-sel">Massa Base (Sponge)</label>
      <select id="sponge-sel" onchange="recalcCake()">
        <option value="red_velvet">Red Velvet Artisanal (Buttermilk &amp; Cacau)</option>
        <option value="pao_de_lo_tradicional">Pão de Ló Tradicional Português</option>
        <option value="chocolate_belga_70">Bolo Húmido de Chocolate Belga 70%</option>
        <option value="amendoa_sem_gluten">Bolo de Amêndoa &amp; Limão (Sem Glúten)</option>
        <option value="nozes_vinho_porto">Bolo Nobre de Noz &amp; Vinho do Porto</option>
      </select>

      <label for="filling-sel">Recheio Refrigerado</label>
      <select id="filling-sel" onchange="recalcCake()">
        <option value="brigadeiro_gourmet">Brigadeiro Gourmet de Chocolate Nobre</option>
        <option value="ovos_moles_doces_conventuais">Doce de Ovos Conventual Português</option>
        <option value="curd_limao_frutos_vermelhos">Lemon Curd &amp; Frutos Vermelhos</option>
        <option value="praline_avela_crocante">Ganache &amp; Praliné de Avelã Piemontesa</option>
        <option value="pistacio_tahini_crocante">Pistácio Siciliano &amp; Crocante de Sésamo</option>
      </select>

      <label for="frosting-sel">Cobertura &amp; Blindagem</label>
      <select id="frosting-sel" onchange="recalcCake()">
        <option value="swiss_meringue_buttercream">Swiss Meringue Buttercream (Cetim / Lambeth)</option>
        <option value="ganache_blindagem_fondant">Blindagem em Ganache + Pasta de Açúcar</option>
        <option value="semi_naked_rustico">Semi-Naked Rústico com Flores Naturais</option>
      </select>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div>
          <label for="primary-color">Cor Cobertura</label>
          <input id="primary-color" type="text" value="#FFFDF9" onchange="recalcCake()" />
        </div>
        <div>
          <label for="accent-color">Cor Debrum / Ouro</label>
          <input id="accent-color" type="text" value="#D4AF37" onchange="recalcCake()" />
        </div>
      </div>

      <label for="iva-sel">Regime Fiscal IVA (Autoridade Tributária PT)</label>
      <select id="iva-sel" onchange="recalcCake()">
        <option value="RESTAURACAO_13">IVA 13% — Serviço de Restauração / Catering (CIVA Lista II)</option>
        <option value="TAKEAWAY_23">IVA 23% — Encomenda Take-Away / Entrega (CIVA Art. 18.º)</option>
      </select>

      <label for="topper-inp">Texto do Topo (Topper Acrílico)</label>
      <input id="topper-inp" type="text" value="Sofia &amp; Miguel" />

      <button type="button" id="btn-calc-cake" class="primary" onclick="recalcCake()">
        Atualizar Modelo 3D, BOM em Gramas &amp; Dossier ASAE
      </button>
    </section>

    <div style="display:grid;gap:18px;">
      <!-- Interactive 3D Stage (Three.js WebGL + Isometric Fallback + X-Ray Dowels Toggle) -->
      <section class="panel" aria-label="Palco Interativo 3D e Engenharia de Estacas">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px;margin-bottom:10px;">
          <h2 style="margin:0;">2. Palco 3D Interativo &amp; Raio-X de Estacas Internas</h2>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;" onclick="toggleXrayDowels()" id="btn-xray">
              🦴 Raio-X Estacas: OFF
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;" onclick="openPrintableASAE()">
              🖨️ Ficha Técnica ASAE A4 ↗
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;border-color:#4f46e5;color:#c7d2fe;" onclick="sendToPastelaria24h()">
              📦 Reservar 24h na InsightPastelaria (:4029)
            </button>
          </div>
        </div>

        <div id="viewport-3d" role="img" aria-label="Visualização 3D Interativa do Bolo Multi-Andar"></div>
        <div id="bridge-feedback" style="margin-top:8px;font-size:12px;color:#6ee7b7;min-height:18px;" aria-live="polite"></div>
      </section>

      <!-- Structured BOM, Dowels, Allergens & Cold-Chain Output (4 Async States, Zero Raw JSON Dump) -->
      <section class="panel" aria-label="Ficha de Produção em Gramas, Alergénios e Frio">
        <h2>3. Capitação em Gramas (BOM), Estacas PP, Alergénios &amp; ControlNet</h2>
        <div id="cake-error-box" class="tile hidden" style="border-color:#f43f5e;color:#fda4af;margin-bottom:12px;"></div>
        <div id="cake-skeleton" class="skeleton hidden"></div>
        <div id="cake-structured-results" style="display:grid;gap:12px;"></div>
      </section>
    </div>
  </div>

  <!-- VIEW 2: ARRHENIUS Q10 SOURDOUGH FERMENTATION & BAKER'S % LAB -->
  <div id="view-ferment" role="tabpanel" aria-labelledby="tab-ferment" class="grid-studio hidden">
    <section class="panel" aria-label="Calculadora Cinética Arrhenius e Percentagem de Padeiro">
      <h2>1. Cinética de Fermentação Natural (Q10) &amp; DDT</h2>
      <label for="ferm-flour">Massa de Farinha Base 100% (g)</label>
      <input id="ferm-flour" type="number" value="5000" min="100" max="500000" />

      <label for="ferm-temp">Temperatura Alvo da Massa — DDT (°C)</label>
      <input id="ferm-temp" type="number" value="26.0" step="0.5" min="4" max="40" />

      <label for="ferm-hyd">Hidratação (%)</label>
      <input id="ferm-hyd" type="number" value="72.0" step="1" min="45" max="105" />

      <label for="ferm-starter">Levain / Massa Mãe (%)</label>
      <input id="ferm-starter" type="number" value="20.0" step="1" min="5" max="50" />

      <button type="button" class="primary" onclick="calcFermentation()">
        Calcular Curva Arrhenius, Água DDT (°C) &amp; Lote HACCP
      </button>
    </section>

    <section class="panel" aria-label="Resultados de Fermentação e Rastreabilidade">
      <h2>2. Escala de Padeiro (g), Tempo de Bloco &amp; Retardo a Frio (+4 °C)</h2>
      <div id="ferment-output" class="tile" style="font-size:13px;color:#cbd5e1;">
        Submeta os parâmetros para calcular a curva cinética Q10 e a temperatura ideal da água.
      </div>
    </section>
  </div>
</main>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" defer onerror="window.__threeOffline=true"></script>
<script>
let tiersState = [
  { diameter_cm: 25, height_cm: 12 },
  { diameter_cm: 20, height_cm: 12 },
  { diameter_cm: 15, height_cm: 14 }
];
let xrayDowels = false;
let lastDesignData = null;
let threeCtx = null;

function announce(msg) {
  const el = document.getElementById('sr-announcer');
  if (el) el.textContent = msg;
}

function toggleMobileDrawer() {
  const tl = document.getElementById('main-tablist');
  const btn = document.getElementById('mobile-menu-btn');
  const isOpen = tl.classList.toggle('open');
  btn.setAttribute('aria-expanded', String(isOpen));
}

function switchMode(mode) {
  const modes = ['cake', 'ferment'];
  modes.forEach(m => {
    const active = m === mode;
    document.getElementById('view-' + m).classList.toggle('hidden', !active);
    const btn = document.getElementById('tab-' + m);
    btn.setAttribute('aria-selected', String(active));
    btn.setAttribute('tabindex', active ? '0' : '-1');
  });
  document.getElementById('main-tablist').classList.remove('open');
  announce(mode === 'cake' ? 'Estúdio 3D Multi-Andar ativo' : 'Laboratório de Fermentação Arrhenius ativo');
  if (mode === 'ferment') calcFermentation();
}

function onTabKeydown(ev) {
  if (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft') return;
  ev.preventDefault();
  const next = document.getElementById('tab-cake').getAttribute('aria-selected') === 'true' ? 'ferment' : 'cake';
  switchMode(next);
  document.getElementById('tab-' + next).focus();
}

function renderTiersEditor() {
  const host = document.getElementById('tiers-editor');
  host.innerHTML = '';
  tiersState.forEach((t, i) => {
    const row = document.createElement('div');
    row.className = 'tier-row';
    row.innerHTML = `
      <div>
        <label for="tdiam-${i}" style="margin-top:2px;">Andar ${i + 1} Ø (cm)</label>
        <input id="tdiam-${i}" type="number" min="8" max="60" value="${t.diameter_cm}" onchange="updateTier(${i}, 'diameter_cm', this.value)" />
      </div>
      <div>
        <label for="theight-${i}" style="margin-top:2px;">Altura (cm)</label>
        <input id="theight-${i}" type="number" min="5" max="30" value="${t.height_cm}" onchange="updateTier(${i}, 'height_cm', this.value)" />
      </div>
      <span style="font-size:11px;color:#94a3b8;padding-bottom:10px;">#${i + 1}</span>
    `;
    host.appendChild(row);
  });
}

function updateTier(idx, field, val) {
  tiersState[idx][field] = Number(val);
  recalcCake();
}

function addTier() {
  if (tiersState.length >= 6) return;
  const topDiam = tiersState[tiersState.length - 1].diameter_cm;
  tiersState.push({ diameter_cm: Math.max(10, topDiam - 5), height_cm: 12 });
  renderTiersEditor();
  recalcCake();
}

function removeTier() {
  if (tiersState.length <= 1) return;
  tiersState.pop();
  renderTiersEditor();
  recalcCake();
}

function toggleXrayDowels() {
  xrayDowels = !xrayDowels;
  document.getElementById('btn-xray').textContent = xrayDowels ? '🦴 Raio-X Estacas: ON' : '🦴 Raio-X Estacas: OFF';
  if (lastDesignData) renderViewport(lastDesignData);
}

function collectCakePayload() {
  return {
    shape: document.getElementById('shape-sel').value,
    tiers: tiersState,
    sponge_key: document.getElementById('sponge-sel').value,
    filling_key: document.getElementById('filling-sel').value,
    frosting_key: document.getElementById('frosting-sel').value,
    primary_color_hex: document.getElementById('primary-color').value || '#FFFDF9',
    accent_color_hex: document.getElementById('accent-color').value || '#D4AF37',
    consumption_mode: document.getElementById('iva-sel').value,
    topper_text: document.getElementById('topper-inp').value || 'Sofia & Miguel'
  };
}

function renderIsometricSvgFallback(data) {
  const stage = document.getElementById('viewport-3d');
  const scene = data.threejs_3d_scene;
  const tiers = scene.tiers || [];
  let yCursor = 285;
  let shapesSvg = `<ellipse cx="220" cy="295" rx="145" ry="14" fill="#334155" />`;

  tiers.forEach(t => {
    const w = Math.max(46, t.diameter_cm * 6.2);
    const h = Math.max(24, t.height_cm * 3.1);
    const x = 220 - w / 2;
    const y = yCursor - h;
    const fillOp = xrayDowels ? '0.28' : '1';
    const rx = scene.shape === 'SQUARE' ? 3 : (scene.shape === 'HEXAGON' ? 6 : 12);
    shapesSvg += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" rx="${rx}" fill="${t.base_color_hex}" fill-opacity="${fillOp}" stroke="${t.piping_accent_color_hex}" stroke-width="2.5"/>`;
    if (scene.shape === 'HEART') {
      shapesSvg += `<text x="220" y="${(y + h / 2 + 5).toFixed(1)}" text-anchor="middle" fill="${t.piping_accent_color_hex}" font-size="14">♥</text>`;
    }
    if (xrayDowels && t.internal_dowels_count > 0) {
      for (let d = 0; d < t.internal_dowels_count; d++) {
        const dx = x + 14 + ((w - 28) * d) / Math.max(1, t.internal_dowels_count - 1);
        shapesSvg += `<line x1="${dx.toFixed(1)}" y1="${(y + 2).toFixed(1)}" x2="${dx.toFixed(1)}" y2="${(y + h - 2).toFixed(1)}" stroke="#38bdf8" stroke-width="3" stroke-dasharray="4 2"/>`;
      }
    }
    yCursor = y;
  });
  if (xrayDowels && tiers.length >= 2) {
    shapesSvg += `<line x1="220" y1="${(yCursor - 8).toFixed(1)}" x2="220" y2="290" stroke="#f43f5e" stroke-width="3.5"/>`;
  }
  const topY = Math.max(22, yCursor - 12);
  shapesSvg += `<text x="220" y="${topY.toFixed(1)}" text-anchor="middle" fill="${tiers[0]?.piping_accent_color_hex || '#d4af37'}" font-size="14" font-weight="700">✨ ${escapeHtml(scene.topper_text)} ✨</text>`;
  stage.innerHTML = `<svg viewBox="0 0 440 320" width="100%" height="100%" role="img" aria-label="Modelo 3D ${scene.tier_count} andares (${scene.shape})">${shapesSvg}</svg>`;
}

function renderViewport(data) {
  if (!window.THREE || window.__threeOffline) {
    renderIsometricSvgFallback(data);
    return;
  }
  try {
    const stage = document.getElementById('viewport-3d');
    if (!threeCtx) {
      stage.innerHTML = '';
      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(stage.clientWidth || 560, 350);
      stage.appendChild(renderer.domElement);
      const scene3 = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(40, (stage.clientWidth || 560) / 350, 0.1, 1000);
      camera.position.set(0, 32, 85);
      camera.lookAt(0, 16, 0);
      const keyLight = new THREE.DirectionalLight(0xffffff, 1.05);
      keyLight.position.set(35, 60, 45);
      scene3.add(keyLight);
      scene3.add(new THREE.AmbientLight(0xcbd5e1, 0.65));
      const group = new THREE.Group();
      scene3.add(group);

      let dragging = false, prevX = 0;
      renderer.domElement.addEventListener('pointerdown', e => { dragging = true; prevX = e.clientX; });
      window.addEventListener('pointerup', () => { dragging = false; });
      window.addEventListener('pointermove', e => {
        if (!dragging) return;
        group.rotation.y += (e.clientX - prevX) * 0.012;
        prevX = e.clientX;
        renderer.render(scene3, camera);
      });
      threeCtx = { renderer, scene3, camera, group };
    }
    const { renderer, scene3, camera, group } = threeCtx;
    while (group.children.length) group.remove(group.children[0]);

    const board = new THREE.Mesh(
      new THREE.CylinderGeometry(22, 22, 1.2, 48),
      new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.4 })
    );
    board.position.y = -0.6;
    group.add(board);

    const sc = data.threejs_3d_scene;
    (sc.tiers || []).forEach(t => {
      const r = t.diameter_cm * 0.5;
      let geom;
      if (sc.shape === 'SQUARE') {
        geom = new THREE.BoxGeometry(t.diameter_cm, t.height_cm, t.diameter_cm);
      } else if (sc.shape === 'HEART') {
        const hs = new THREE.Shape();
        const s = r * 0.095;
        hs.moveTo(0, -5 * s);
        hs.bezierCurveTo(6 * s, -1 * s, 10 * s, 5 * s, 5 * s, 9 * s);
        hs.bezierCurveTo(2 * s, 11 * s, 0, 8 * s, 0, 6 * s);
        hs.bezierCurveTo(0, 8 * s, -2 * s, 11 * s, -5 * s, 9 * s);
        hs.bezierCurveTo(-10 * s, 5 * s, -6 * s, -1 * s, 0, -5 * s);
        geom = new THREE.ExtrudeGeometry(hs, { depth: t.height_cm, bevelEnabled: true, bevelThickness: 0.35, bevelSize: 0.35 });
        geom.rotateX(Math.PI / 2);
        geom.translate(0, t.height_cm / 2, 0);
      } else {
        const segs = sc.shape === 'HEXAGON' ? 6 : 64;
        geom = new THREE.CylinderGeometry(r, r, t.height_cm, segs);
      }
      const mat = new THREE.MeshStandardMaterial({
        color: t.base_color_hex || '#FFFDF9',
        transparent: xrayDowels,
        opacity: xrayDowels ? 0.32 : 1.0,
        roughness: 0.55
      });
      const mesh = new THREE.Mesh(geom, mat);
      mesh.position.y = t.position_y_cm;
      group.add(mesh);

      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(r * 0.99, 0.32, 12, sc.shape === 'HEXAGON' ? 6 : 48),
        new THREE.MeshStandardMaterial({ color: t.piping_accent_color_hex || '#D4AF37', metalness: 0.45, roughness: 0.3 })
      );
      ring.rotation.x = Math.PI / 2;
      ring.position.y = t.position_y_cm + t.height_cm / 2;
      group.add(ring);

      if (xrayDowels && t.internal_dowels_count > 0) {
        for (let i = 0; i < t.internal_dowels_count; i++) {
          const ang = (i / t.internal_dowels_count) * Math.PI * 2;
          const dr = r * 0.48;
          const dowel = new THREE.Mesh(
            new THREE.CylinderGeometry(0.35, 0.35, t.height_cm, 12),
            new THREE.MeshStandardMaterial({ color: 0x38bdf8 })
          );
          dowel.position.set(Math.cos(ang) * dr, t.position_y_cm, Math.sin(ang) * dr);
          group.add(dowel);
        }
      }
    });
    renderer.render(scene3, camera);
  } catch (_) {
    renderIsometricSvgFallback(data);
  }
}

function escapeHtml(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

async function recalcCake() {
  const errBox = document.getElementById('cake-error-box');
  const skel = document.getElementById('cake-skeleton');
  const out = document.getElementById('cake-structured-results');
  const btn = document.getElementById('btn-calc-cake');
  errBox.classList.add('hidden');
  skel.classList.remove('hidden');
  btn.disabled = true;

  try {
    const r = await fetch('/api/bake/design', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(collectCakePayload())
    });
    const data = await r.json();
    if (!r.ok || !data.ok) {
      throw new Error(data.error || ('HTTP ' + r.status));
    }
    lastDesignData = data;
    const p = data.pricing_and_at_invoicing;
    const st = data.portions_and_structure;
    const al = data.allergens_eu_1169_2011;
    const bom = data.recipe_bom_grams;
    const cold = data.logistics_and_haccp_cold_chain;

    document.getElementById('hero-price').textContent = '€' + p.recommended_client_total_gross_eur.toFixed(2);
    document.getElementById('hero-atcud').textContent = `Sinal 50%: €${p.deposit_50pct_atcud_invoice_eur.toFixed(2)} · IVA ${p.iva_rate_pct}% · ${p.atcud_preview}`;
    document.getElementById('kpi-portions').textContent = `${st.wedding_portions_2_5x5cm} / ${st.party_portions_5x5cm}`;
    document.getElementById('kpi-weight').textContent = `${st.total_assembled_weight_kg} kg`;
    document.getElementById('kpi-box').textContent = cold.required_transport_box_cm;
    document.getElementById('kpi-allergen-count').textContent = `${al.allergen_codes.length} Anexo II`;

    const ingRows = Object.entries(bom.sponge_ingredients_g || {}).map(([k, v]) =>
      `<tr><td>${escapeHtml(k)}</td><td>Massa (${escapeHtml(bom.sponge_type)})</td><td style="text-align:right;font-weight:600;color:#6ee7b7;">${Number(v).toFixed(1)} g</td></tr>`
    ).join('');

    const dowelRows = (st.tier_dowel_blueprint || []).map(d =>
      `<li>Andar ${d.tier_index} (${d.tier_diameter_cm} cm): <strong>${d.polypropylene_dowel_rods_count} estacas PP</strong> cortadas a ${d.dowel_cut_height_cm} cm + prato ${d.cake_board_under_upper_tier_cm} cm</li>`
    ).join('') || '<li>Andar único estável — sem estacas internas necessárias.</li>';

    const allergenPills = (al.mandatory_client_label || []).map(a =>
      `<span class="badge badge-allergen">Anexo II #${a.anexo_ii_num}: ${escapeHtml(a.code)}</span>`
    ).join('');

    out.innerHTML = `
      <div class="tile">
        <div style="font-size:12px;font-weight:600;color:#e2e8f0;">Alergénios Obrigatórios Declarados (Reg. UE 1169/2011 &amp; DL 26/2016)</div>
        <div style="margin-top:6px;">${allergenPills}</div>
        <div style="margin-top:6px;font-size:11px;color:#fde68a;">${escapeHtml(al.allergen_counter_signage_pt)}</div>
      </div>
      <div class="tile">
        <div style="font-size:12px;font-weight:600;color:#e2e8f0;">Receituário Escalado ao Grama (BOM Total: ${(bom.sponge_total_g + bom.filling_total_g + bom.frosting_total_g).toFixed(0)} g)</div>
        <table class="bom-table mobile-card-table">
          <thead><tr><th>Componente</th><th>Camada</th><th style="text-align:right;">Peso Líquido</th></tr></thead>
          <tbody>
            ${ingRows}
            <tr><td>${escapeHtml(bom.filling_type)}</td><td>Recheio (+4 °C)</td><td style="text-align:right;font-weight:600;color:#93c5fd;">${bom.filling_total_g.toFixed(1)} g</td></tr>
            <tr><td>${escapeHtml(bom.frosting_type)}</td><td>Cobertura (Máx ${cold.max_safe_ambient_display_temp_c} °C)</td><td style="text-align:right;font-weight:600;color:#c4b5fd;">${bom.frosting_total_g.toFixed(1)} g</td></tr>
          </tbody>
        </table>
      </div>
      <div class="tile">
        <div style="font-size:12px;font-weight:600;color:#e2e8f0;">Planta de Estacas Internas &amp; Transporte Refrigerado</div>
        <ul style="margin:6px 0 0;padding-left:18px;font-size:12px;color:#cbd5e1;">
          ${dowelRows}
          <li>Transporte Frio: <strong>${escapeHtml(cold.refrigerated_van_target_temp_c)}</strong> · Força-G máx: ${cold.max_safe_cornering_g_force} g</li>
        </ul>
      </div>
      <div class="tile">
        <div style="font-size:12px;font-weight:600;color:#e2e8f0;">Especificação Studio Render (ControlNet Depth ${data.comfyui_controlnet_render.controlnet_depth_strength})</div>
        <p style="margin:6px 0 0;font-size:12px;color:#94a3b8;max-width:68ch;line-height:1.5;">${escapeHtml(data.comfyui_controlnet_render.positive_prompt)}</p>
      </div>
    `;
    renderViewport(data);
    announce(`Bolo 3D atualizado: ${st.wedding_portions_2_5x5cm} fatias, €${p.recommended_client_total_gross_eur.toFixed(2)}.`);
  } catch (err) {
    errBox.classList.remove('hidden');
    errBox.innerHTML = `<strong>Não foi possível validar a geometria (${escapeHtml(err.message)}).</strong>
      <button type="button" class="secondary" style="margin-left:10px;padding:4px 10px;" onclick="recalcCake()">↻ Tentar Novamente</button>`;
    announce('Erro de validação estrutural: ' + err.message);
  } finally {
    skel.classList.add('hidden');
    btn.disabled = false;
  }
}

function openPrintableASAE() {
  const p = collectCakePayload();
  const qs = new URLSearchParams({
    shape: p.shape,
    sponge_key: p.sponge_key,
    filling_key: p.filling_key,
    frosting_key: p.frosting_key,
    topper_text: p.topper_text,
    consumption_mode: p.consumption_mode
  });
  window.open('/api/bake/ficha-asae/print?' + qs.toString(), '_blank', 'noopener');
}

async function sendToPastelaria24h() {
  const fb = document.getElementById('bridge-feedback');
  fb.style.color = '#a5b4fc';
  fb.textContent = 'A enviar encomenda 24h e Ficha ASAE para InsightPastelaria (:4029)...';
  try {
    const r = await fetch('/api/bake/reserve-pastelaria', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(collectCakePayload())
    });
    const d = await r.json();
    if (!r.ok || !d.ok) throw new Error(d.error || 'Falha na ponte');
    fb.style.color = '#6ee7b7';
    const modeMsg = d.bridge_mode === 'LIVE_HTTP_4029'
      ? `✓ Encomenda 24h registada ao vivo na InsightPastelaria (${d.pastelaria_reservation.reservation.reservation_id})!`
      : `✓ Pacote 24h & Ficha ASAE preparados (modo autónomo — inicie :4029 para sincronização direta).`;
    fb.textContent = modeMsg;
    announce(modeMsg);
  } catch (e) {
    fb.style.color = '#fda4af';
    fb.textContent = 'Erro ao comunicar: ' + e.message;
  }
}

async function calcFermentation() {
  const out = document.getElementById('ferment-output');
  out.innerHTML = '<div class="skeleton"></div>';
  try {
    const r = await fetch('/api/bake/fermentation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        flour_mass_g: Number(document.getElementById('ferm-flour').value || 5000),
        dough_temp_c: Number(document.getElementById('ferm-temp').value || 26),
        hydration_pct: Number(document.getElementById('ferm-hyd').value || 72),
        starter_pct: Number(document.getElementById('ferm-starter').value || 20)
      })
    });
    const d = await r.json();
    if (!r.ok || !d.ok) throw new Error(d.error || 'Parâmetros inválidos');
    const b = d.bakers_percentage_bom_grams;
    const k = d.arrhenius_fermentation_kinetics;
    out.innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:12px;">
        <div class="panel"><div style="font-size:11px;color:#94a3b8;">Fermentação em Bloco</div><div style="font-size:22px;font-weight:700;color:#6ee7b7;">${k.estimated_bulk_fermentation_hours} h</div><div style="font-size:11px;color:#94a3b8;">(${k.estimated_bulk_fermentation_minutes} min a ${k.target_dough_temp_c} °C)</div></div>
        <div class="panel"><div style="font-size:11px;color:#94a3b8;">Água Necessária (DDT)</div><div style="font-size:22px;font-weight:700;color:#93c5fd;">${k.required_water_temp_ddt_c} °C</div><div style="font-size:11px;color:#94a3b8;">Regra 3 Fatores</div></div>
        <div class="panel"><div style="font-size:11px;color:#94a3b8;">Massa Total Escalada</div><div style="font-size:22px;font-weight:700;color:#f8fafc;">${b.total_dough_mass_kg} kg</div><div style="font-size:11px;color:#94a3b8;">Custo Lote: €${b.raw_batch_cost_eur.toFixed(2)}</div></div>
      </div>
      <div style="font-size:12px;color:#cbd5e1;line-height:1.6;">
        <strong>Fórmula Padeiro:</strong> Farinha ${b.flour_100pct_g} g · Água ${b.water_g} g (${b.hydration_pct}%) · Levain ${b.levain_starter_g} g (${b.starter_pct}%) · Sal ${b.salt_g} g (${b.salt_pct}%)<br/>
        <strong>Perfil Sensorial:</strong> ${escapeHtml(k.lactic_to_acetic_profile)} · Retardo +${k.cold_retard_temp_c} °C (${k.cold_retard_hours}h ≈ ${k.cold_retard_24c_equivalent_hours}h equiv.)<br/>
        <span style="font-family:monospace;font-size:11px;color:#94a3b8;">SHA-256 HACCP: ${d.haccp_and_bitemporal_traceability.sha256_audit_receipt.slice(0, 24)}…</span>
      </div>
    `;
  } catch (e) {
    out.innerHTML = `<span style="color:#fda4af;">Erro: ${escapeHtml(e.message)}</span> <button type="button" class="secondary" onclick="calcFermentation()">↻ Retry</button>`;
  }
}

renderTiersEditor();
recalcCake();
</script>
</body>
</html>"""


def create_insight_bake_router() -> APIRouter:
    engine = InsightBakeEngine()
    router = APIRouter(tags=["InsightBake"])

    @router.get("/status")
    def get_status() -> Dict[str, Any]:
        return engine.get_status()

    @router.get("/studio", response_class=HTMLResponse)
    def get_interactive_3d_studio() -> HTMLResponse:
        return HTMLResponse(content=INTERACTIVE_3D_CAKE_STUDIO_HTML)

    @router.post("/design")
    @router.post("/execute")
    def execute_action(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.execute(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/fermentation")
    def execute_fermentation(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        body = dict(payload or {})
        body["action"] = "fermentation"
        res = engine.execute(body)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.get("/ficha-asae/print", response_class=HTMLResponse)
    def print_cake_asae_ficha(
        shape: str = Query(default="ROUND"),
        sponge_key: str = Query(default="red_velvet"),
        filling_key: str = Query(default="brigadeiro_gourmet"),
        frosting_key: str = Query(default="swiss_meringue_buttercream"),
        topper_text: str = Query(default="Sofia & Miguel"),
        consumption_mode: str = Query(default="RESTAURACAO_13"),
    ) -> HTMLResponse:
        res = engine.execute(
            {
                "shape": shape,
                "sponge_key": sponge_key,
                "filling_key": filling_key,
                "frosting_key": frosting_key,
                "topper_text": topper_text,
                "consumption_mode": consumption_mode,
            }
        )
        if not res.get("ok"):
            return HTMLResponse(status_code=400, content=f"<h1>Erro Estrutural: {res.get('error')}</h1>")
        return HTMLResponse(content=render_cake_asae_ficha_html(res))

    @router.post("/reserve-pastelaria")
    def reserve_custom_cake_in_pastelaria(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.dispatch_custom_cake_to_pastelaria(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/scrub")
    def scrub_text(payload: Dict[str, Any] = Body(default={})) -> Dict[str, Any]:
        return engine.scrub_input(str(payload.get("text", "")))

    @router.get("/widget.js")
    def get_web_component_js() -> Response:
        js = """
(function() {
  if (typeof window === 'undefined' || customElements.get('insight-bake')) return;
  class InsightBakeWidget extends HTMLElement {
    connectedCallback() {
      const apiBase = this.getAttribute('api-base') || '/api/bake';
      this.innerHTML = `
        <section role="region" aria-label="SetMiddle Insight™ · Bake" style="background:#0f172a;color:#f8fafc;border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:16px;font-family:Inter,system-ui,sans-serif;font-variant-numeric:tabular-nums;">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">
            <h3 style="margin:0;font-size:15px;font-weight:600;">SetMiddle Insight™ · Bake (3D Cake Studio &amp; Arrhenius Q10)</h3>
            <a href="${apiBase}/studio" target="_blank" rel="noopener" style="color:#818cf8;font-size:12px;font-weight:600;text-decoration:none;">Abrir Estúdio 3D ↗</a>
          </div>
          <div data-bake-status aria-live="polite" style="font-size:12px;color:#94a3b8;margin-top:6px;">A sincronizar estado em ${apiBase}/status…</div>
        </section>`;
      const st = this.querySelector('[data-bake-status]');
      fetch(apiBase + '/status')
        .then(r => r.json())
        .then(d => {
          if (st && d.ok) st.textContent = `Online (v${d.version}) · ${d.available_shapes.length} Formatos 3D · ${d.eu_14_allergens_supported} Alergénios UE 1169/2011`;
        })
        .catch(() => {
          if (st) st.textContent = `Modo autónomo em ${apiBase} · Pronto para cálculo 3D & Arrhenius`;
        });
    }
  }
  customElements.define('insight-bake', InsightBakeWidget);
})();
""".strip()
        return Response(content=js, media_type="application/javascript")

    return router


def mount_insight_bake_plugin(app: FastAPI, prefix: str = "/api/bake") -> bool:
    app.include_router(create_insight_bake_router(), prefix=prefix)
    return True

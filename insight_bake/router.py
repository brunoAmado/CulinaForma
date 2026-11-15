"""
FastAPI `APIRouter` Plugin for `SetMiddle Insight™ · Bake` (`insight_bake.router`).
Can be mounted standalone (`:4030`) or inside `ChronicleRAG` (`:8765`).
Enforces UX Engine 2.8, WCAG 2.2 AA/AAA & Portugal Decreto-Lei n.º 82/2022.
"""

from __future__ import annotations

import urllib.parse
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import APIRouter, Body, FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response

from insight_bake.engine import (
    InsightBakeEngine,
    build_bake_asae_ficha_tecnica,
    compute_arrhenius_fermentation_and_bakers_pct,
    render_cake_asae_ficha_html,
    render_cake_asae_ficha_pdf_bytes,
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
      <button id="tab-estab" class="tab-btn" role="tab" aria-selected="false" aria-controls="view-estab" tabindex="-1" onclick="switchMode('estab')">
        🏛️ Estabelecimento ASAE
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
      <h2>1. Geometria 3D (1 a 6 Andares) &amp; Sabores por Andar</h2>

      <div class="tile" style="margin-bottom:12px;">
        <label for="recipe-search-inp" style="margin-top:0;">🔍 Pesquisa Semântica &amp; Restrições (ex.: sem glúten verão 26°C 60 pessoas)</label>
        <div style="display:flex;gap:6px;">
          <input id="recipe-search-inp" type="text" placeholder="Ex: sem glúten casamento 60 pessoas" />
          <button type="button" class="secondary" style="white-space:nowrap;" onclick="runSemanticRecipeSearch()">Pesquisar</button>
        </div>
        <div id="recipe-search-results" style="margin-top:8px;font-size:12px;color:#94a3b8;"></div>
      </div>

      <label for="shape-sel">Formato Geométrico 3D</label>
      <select id="shape-sel" onchange="recalcCake()">
        <option value="ROUND">Redondo Clássico (Cylinder 64-Seg)</option>
        <option value="SQUARE">Quadrado Contemporâneo (Box)</option>
        <option value="HEART">Coração Romântico (Parametric Heart)</option>
        <option value="HEXAGON">Hexagonal Geométrico (6 Faces)</option>
      </select>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px;">
        <span style="font-size:12px;font-weight:600;color:#cbd5e1;">Andares Empilhados (Base → Topo · Sabores Mistos)</span>
        <div style="display:flex;gap:6px;">
          <button type="button" class="secondary" style="padding:5px 10px;font-size:12px;" onclick="addTier()">+ Andar</button>
          <button type="button" class="secondary" style="padding:5px 10px;font-size:12px;" onclick="removeTier()">− Andar</button>
        </div>
      </div>
      <div id="tiers-editor" style="margin-top:8px;"></div>

      <label for="sponge-sel">Massa Base Padrão (Sponge)</label>
      <select id="sponge-sel" onchange="recalcCake()">
        <option value="red_velvet">Red Velvet Artisanal (Buttermilk &amp; Cacau)</option>
        <option value="pao_de_lo_tradicional">Pão de Ló Tradicional Português</option>
        <option value="chocolate_belga_70">Bolo Húmido de Chocolate Belga 70%</option>
        <option value="amendoa_sem_gluten">Bolo de Amêndoa &amp; Limão (Sem Glúten)</option>
        <option value="nozes_vinho_porto">Bolo Nobre de Noz &amp; Vinho do Porto</option>
      </select>

      <label for="filling-sel">Recheio Refrigerado Padrão</label>
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

      <label for="country-sel">Jurisdição / Locale Fiscal</label>
      <select id="country-sel" onchange="recalcCake()">
        <option value="PT">PT — Portugal (EUR · CIVA / Art. 53.º)</option>
        <option value="ES">ES — España (EUR · Franquicia PYMES)</option>
        <option value="FR">FR — France (EUR · Art. 293 B CGI)</option>
        <option value="DE">DE — Deutschland (EUR · § 19 UStG)</option>
        <option value="IT">IT — Italia (EUR · Regime Forfettario)</option>
        <option value="GB">GB — United Kingdom (GBP · HMRC SME)</option>
        <option value="BR">BR — Brasil (BRL · MEI SIMEI)</option>
        <option value="US">US — United States (USD · Small Seller)</option>
      </select>

      <label for="iva-sel">Regime Fiscal (Standard vs. Isenção PME / ENI)</label>
      <select id="iva-sel" onchange="recalcCake()">
        <option value="RESTAURACAO_13">Taxa Restauração / Catering (PT 13% / Local)</option>
        <option value="TAKEAWAY_23">Taxa Standard / Take-Away (PT 23% / Local)</option>
        <option value="EXEMPT_SMALL_BUSINESS">Isento PME / ENI 0% (M10 / Art. 293B / §19 / MEI + CMV Bruto)</option>
      </select>

      <label for="topper-inp">Texto do Topo (Topper Acrílico)</label>
      <input id="topper-inp" type="text" value="Sofia &amp; Miguel" />

      <button type="button" id="btn-calc-cake" class="primary" onclick="recalcCake()">
        Atualizar Modelo 3D, BOM em Gramas &amp; Dossier ASAE
      </button>
    </section>

    <div style="display:grid;gap:18px;">
      <!-- Interactive 3D Stage (Three.js WebGL + Cutaway Cross-Section + X-Ray Dowels + Async Render + Fiscal Checkout) -->
      <section class="panel" aria-label="Palco Interativo 3D e Engenharia de Estacas">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px;margin-bottom:10px;">
          <h2 style="margin:0;">2. Palco 3D, Corte Transversal &amp; Faturação Sinal 50%</h2>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;" onclick="toggleCutawaySlice()" id="btn-cutaway">
              🔪 Corte Transversal: OFF
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;" onclick="toggleXrayDowels()" id="btn-xray">
              🦴 Raio-X Estacas: OFF
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;border-color:#0284c7;color:#7dd3fc;" onclick="enqueueAsyncComfyRender()" id="btn-render-async">
              🎨 Render Studio Assíncrono
            </button>
            <button type="button" class="secondary hidden" style="padding:6px 10px;font-size:12px;border-color:#f43f5e;color:#fda4af;" onclick="cancelActiveRenderJob()" id="btn-render-cancel">
              ⏹ Cancelar Render
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;" onclick="openPrintableASAE()">
              🖨️ Ficha ASAE A4 ↗
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;border-color:#059669;color:#6ee7b7;" onclick="downloadBakeAsaePdf()">
              ⬇️ PDF A4 ASAE
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;border-color:#eab308;color:#fde047;" onclick="generateDepositMultibanco()">
              💳 Sinal 50% MB / SAF-T PT
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;border-color:#ec4899;color:#f9a8d4;" onclick="createClientQuotePortal()">
              🔗 Link Proposta Cliente
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;border-color:#14b8a6;color:#5eead4;" onclick="dispatchFleetColdChain()">
              🚚 Guia AT &amp; Frota Frio
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;border-color:#f97316;color:#fdba74;" onclick="downloadCateringCuttingPdf()">
              🍽️ PDF Guia Corte &amp; Cavilhas
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;border-color:#a855f7;color:#d8b4fe;" onclick="runDietarySafeReformulation()">
              🌾 Sem Glúten / Vegan
            </button>
            <button type="button" class="secondary" style="padding:6px 10px;font-size:12px;border-color:#4f46e5;color:#c7d2fe;" onclick="sendToPastelaria24h()">
              📦 Reservar 24h (:4029)
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

  <!-- VIEW 3: OFFICIAL ASAE ESTABLISHMENT IDENTIFICATION -->
  <div id="view-estab" role="tabpanel" aria-labelledby="tab-estab" class="grid-studio hidden">
    <section class="panel" aria-label="Identificação Oficial do Operador Económico ASAE">
      <h2>1. Operador Económico &amp; NIF Módulo-11 (ASAE / DGAV)</h2>
      <label for="estab-denom">Denominação Social</label>
      <input id="estab-denom" type="text" value="" />

      <label for="estab-nome">Nome Comercial / Insígnia</label>
      <input id="estab-nome" type="text" value="" />

      <label for="estab-nif">NIF Português (9 dígitos — Validação Módulo-11)</label>
      <input id="estab-nif" type="text" maxlength="9" value="" />

      <label for="estab-cae">CAE Principal</label>
      <input id="estab-cae" type="text" value="" />

      <button type="button" class="primary" onclick="saveEstablishmentBake()">
        Guardar e Carimbar Todas as Fichas A4 &amp; PDFs
      </button>
    </section>

    <section class="panel" aria-label="Licenciamento RJACSR e Responsável HACCP">
      <h2>2. Morada, Licença RJACSR/DGAV &amp; Responsável HACCP</h2>
      <label for="estab-morada">Morada Completa do Estabelecimento</label>
      <input id="estab-morada" type="text" value="" />

      <label for="estab-licenca">Licença RJACSR (DL n.º 10/2015) / NCV DGAV</label>
      <input id="estab-licenca" type="text" value="" />

      <label for="estab-haccp">Responsável Técnico de Autocontrolo HACCP</label>
      <input id="estab-haccp" type="text" value="" />

      <label for="estab-contacto">Contacto Dístico Alergénios (DL n.º 26/2016)</label>
      <input id="estab-contacto" type="text" value="" />

      <div id="estab-feedback" class="tile" style="margin-top:14px;font-size:12px;color:#94a3b8;" aria-live="polite">
        Partilhado com InsightPastelaria (:4029) — carimbado automaticamente nos PDFs A4 de Bolos 3D, Fermentação Natural e Quadro dos 14 Alergénios.
      </div>
    </section>
  </div>
</main>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" defer onerror="window.__threeOffline=true"></script>
<script>
let tiersState = [
  { diameter_cm: 25, height_cm: 12, sponge_key: '', filling_key: '' },
  { diameter_cm: 20, height_cm: 12, sponge_key: '', filling_key: '' },
  { diameter_cm: 15, height_cm: 14, sponge_key: '', filling_key: '' }
];
let xrayDowels = false;
let cutawaySlice = false;
let activeRenderJobId = null;
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
  const modes = ['cake', 'ferment', 'estab'];
  modes.forEach(m => {
    const active = m === mode;
    document.getElementById('view-' + m).classList.toggle('hidden', !active);
    const btn = document.getElementById('tab-' + m);
    btn.setAttribute('aria-selected', String(active));
    btn.setAttribute('tabindex', active ? '0' : '-1');
  });
  document.getElementById('main-tablist').classList.remove('open');
  const labels = {
    cake: 'Estúdio 3D Multi-Andar ativo',
    ferment: 'Laboratório de Fermentação Arrhenius ativo',
    estab: 'Identificação Oficial do Estabelecimento ASAE ativa'
  };
  announce(labels[mode] || 'Modo atualizado');
  if (mode === 'ferment') calcFermentation();
  if (mode === 'estab') loadEstablishmentBake();
}

function onTabKeydown(ev) {
  if (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft') return;
  ev.preventDefault();
  const modes = ['cake', 'ferment', 'estab'];
  const curIdx = modes.findIndex(m => document.getElementById('tab-' + m).getAttribute('aria-selected') === 'true');
  const delta = ev.key === 'ArrowRight' ? 1 : -1;
  const next = modes[(curIdx + delta + modes.length) % modes.length];
  switchMode(next);
  document.getElementById('tab-' + next).focus();
}

function renderTiersEditor() {
  const host = document.getElementById('tiers-editor');
  host.innerHTML = '';
  tiersState.forEach((t, i) => {
    const row = document.createElement('div');
    row.className = 'tile';
    row.style.marginBottom = '8px';
    row.innerHTML = `
      <div class="tier-row" style="margin-bottom:4px;">
        <div>
          <label for="tdiam-${i}" style="margin-top:2px;">Andar ${i + 1} Ø (cm)</label>
          <input id="tdiam-${i}" type="number" min="8" max="60" value="${t.diameter_cm}" onchange="updateTier(${i}, 'diameter_cm', this.value)" />
        </div>
        <div>
          <label for="theight-${i}" style="margin-top:2px;">Altura (cm)</label>
          <input id="theight-${i}" type="number" min="5" max="30" value="${t.height_cm}" onchange="updateTier(${i}, 'height_cm', this.value)" />
        </div>
        <span style="font-size:11px;color:#94a3b8;padding-bottom:10px;">#${i + 1}</span>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
        <div>
          <label for="tsponge-${i}" style="margin-top:2px;font-size:11px;">Massa Andar #${i + 1}</label>
          <select id="tsponge-${i}" style="font-size:12px;padding:6px;" onchange="updateTierStr(${i}, 'sponge_key', this.value)">
            <option value="" ${!t.sponge_key ? 'selected' : ''}>Padrão Geral</option>
            <option value="red_velvet" ${t.sponge_key === 'red_velvet' ? 'selected' : ''}>Red Velvet</option>
            <option value="pao_de_lo_tradicional" ${t.sponge_key === 'pao_de_lo_tradicional' ? 'selected' : ''}>Pão de Ló</option>
            <option value="chocolate_belga_70" ${t.sponge_key === 'chocolate_belga_70' ? 'selected' : ''}>Choc. Belga 70%</option>
            <option value="amendoa_sem_gluten" ${t.sponge_key === 'amendoa_sem_gluten' ? 'selected' : ''}>Amêndoa S/ Glúten</option>
            <option value="nozes_vinho_porto" ${t.sponge_key === 'nozes_vinho_porto' ? 'selected' : ''}>Noz &amp; Porto</option>
          </select>
        </div>
        <div>
          <label for="tfill-${i}" style="margin-top:2px;font-size:11px;">Recheio Andar #${i + 1}</label>
          <select id="tfill-${i}" style="font-size:12px;padding:6px;" onchange="updateTierStr(${i}, 'filling_key', this.value)">
            <option value="" ${!t.filling_key ? 'selected' : ''}>Padrão Geral</option>
            <option value="brigadeiro_gourmet" ${t.filling_key === 'brigadeiro_gourmet' ? 'selected' : ''}>Brigadeiro</option>
            <option value="ovos_moles_doces_conventuais" ${t.filling_key === 'ovos_moles_doces_conventuais' ? 'selected' : ''}>Doce de Ovos</option>
            <option value="curd_limao_frutos_vermelhos" ${t.filling_key === 'curd_limao_frutos_vermelhos' ? 'selected' : ''}>Lemon Curd</option>
            <option value="praline_avela_crocante" ${t.filling_key === 'praline_avela_crocante' ? 'selected' : ''}>Praliné Avelã</option>
            <option value="pistacio_tahini_crocante" ${t.filling_key === 'pistacio_tahini_crocante' ? 'selected' : ''}>Pistácio &amp; Sésamo</option>
          </select>
        </div>
      </div>
    `;
    host.appendChild(row);
  });
}

function updateTier(idx, field, val) {
  tiersState[idx][field] = Number(val);
  recalcCake();
}

function updateTierStr(idx, field, val) {
  tiersState[idx][field] = String(val || '');
  recalcCake();
}

function addTier() {
  if (tiersState.length >= 6) return;
  const topDiam = tiersState[tiersState.length - 1].diameter_cm;
  tiersState.push({ diameter_cm: Math.max(10, topDiam - 5), height_cm: 12, sponge_key: '', filling_key: '' });
  renderTiersEditor();
  recalcCake();
}

function removeTier() {
  if (tiersState.length <= 1) return;
  tiersState.pop();
  renderTiersEditor();
  recalcCake();
}

function toggleCutawaySlice() {
  cutawaySlice = !cutawaySlice;
  document.getElementById('btn-cutaway').textContent = cutawaySlice ? '🔪 Corte Transversal: ON' : '🔪 Corte Transversal: OFF';
  if (lastDesignData) renderViewport(lastDesignData);
}

function toggleXrayDowels() {
  xrayDowels = !xrayDowels;
  document.getElementById('btn-xray').textContent = xrayDowels ? '🦴 Raio-X Estacas: ON' : '🦴 Raio-X Estacas: OFF';
  if (lastDesignData) renderViewport(lastDesignData);
}

function collectCakePayload() {
  const cleanTiers = tiersState.map(t => {
    const item = { diameter_cm: t.diameter_cm, height_cm: t.height_cm };
    if (t.sponge_key) item.sponge_key = t.sponge_key;
    if (t.filling_key) item.filling_key = t.filling_key;
    return item;
  });
  return {
    shape: document.getElementById('shape-sel').value,
    tiers: cleanTiers,
    sponge_key: document.getElementById('sponge-sel').value,
    filling_key: document.getElementById('filling-sel').value,
    frosting_key: document.getElementById('frosting-sel').value,
    primary_color_hex: document.getElementById('primary-color').value || '#FFFDF9',
    accent_color_hex: document.getElementById('accent-color').value || '#D4AF37',
    consumption_mode: document.getElementById('iva-sel').value,
    country_code: (document.getElementById('country-sel') ? document.getElementById('country-sel').value : 'PT'),
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
    if (cutawaySlice && Array.isArray(t.cutaway_layers)) {
      let ly = y + 3;
      const innerH = h - 6;
      const totalCm = t.cutaway_layers.reduce((acc, c) => acc + c.height_cm, 0) || 1;
      t.cutaway_layers.forEach(cl => {
        const bandH = (cl.height_cm / totalCm) * innerH;
        shapesSvg += `<rect x="220" y="${ly.toFixed(1)}" width="${(w / 2 - 4).toFixed(1)}" height="${bandH.toFixed(1)}" fill="${cl.color_hex}" opacity="0.95"/>`;
        ly += bandH;
      });
    }
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
      const thetaLen = cutawaySlice ? Math.PI * 1.52 : Math.PI * 2;
      let geom;
      if (sc.shape === 'SQUARE' && !cutawaySlice) {
        geom = new THREE.BoxGeometry(t.diameter_cm, t.height_cm, t.diameter_cm);
      } else if (sc.shape === 'HEART' && !cutawaySlice) {
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
        geom = new THREE.CylinderGeometry(r, r, t.height_cm, segs, 1, false, 0, thetaLen);
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

      if (cutawaySlice && Array.isArray(t.cutaway_layers)) {
        let localY = t.position_y_cm - (t.height_cm / 2) + 0.25;
        t.cutaway_layers.forEach(cl => {
          const innerDisc = new THREE.Mesh(
            new THREE.CylinderGeometry(r * 0.94, r * 0.94, cl.height_cm * 0.95, 48),
            new THREE.MeshStandardMaterial({ color: cl.color_hex, roughness: 0.7 })
          );
          innerDisc.position.y = localY + (cl.height_cm / 2);
          group.add(innerDisc);
          localY += cl.height_cm;
        });
      }

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
    const nut = data.nutritional_declaration_eu_1169;
    const bom = data.recipe_bom_grams;
    const cold = data.logistics_and_haccp_cold_chain;

    document.getElementById('hero-price').textContent = '€' + p.recommended_client_total_gross_eur.toFixed(2);
    document.getElementById('hero-atcud').textContent = `Sinal 50%: €${p.deposit_50pct_atcud_invoice_eur.toFixed(2)} · MB ${p.multibanco_entity}/${p.multibanco_ref_50pct} · ${p.atcud_preview}`;
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

    const nutHtml = nut ? `
      <div class="tile">
        <div style="font-size:12px;font-weight:600;color:#e2e8f0;">Declaração Nutricional Obrigatória (${escapeHtml(nut.regulation)})</div>
        <table class="bom-table mobile-card-table">
          <thead><tr><th>Nutriente</th><th style="text-align:right;">Por 100 g</th><th style="text-align:right;">${escapeHtml(nut.portion_label_pt)} (${nut.portion_weight_g} g)</th></tr></thead>
          <tbody>
            <tr><td>Energia</td><td style="text-align:right;font-weight:600;">${nut.per_100g.energy_kj} kJ / ${nut.per_100g.energy_kcal} kcal</td><td style="text-align:right;">${nut.per_portion.energy_kj} kJ / ${nut.per_portion.energy_kcal} kcal</td></tr>
            <tr><td>Lípidos (dos quais saturados)</td><td style="text-align:right;">${nut.per_100g.fat_g} g (${nut.per_100g.saturates_g} g)</td><td style="text-align:right;">${nut.per_portion.fat_g} g (${nut.per_portion.saturates_g} g)</td></tr>
            <tr><td>Hidratos de Carbono (açúcares)</td><td style="text-align:right;">${nut.per_100g.carbs_g} g (${nut.per_100g.sugars_g} g)</td><td style="text-align:right;">${nut.per_portion.carbs_g} g (${nut.per_portion.sugars_g} g)</td></tr>
            <tr><td>Proteínas · Sal</td><td style="text-align:right;">${nut.per_100g.protein_g} g · ${nut.per_100g.salt_g} g</td><td style="text-align:right;">${nut.per_portion.protein_g} g · ${nut.per_portion.salt_g} g</td></tr>
          </tbody>
        </table>
      </div>
    ` : '';

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
      ${nutHtml}
      <div class="tile">
        <div style="font-size:12px;font-weight:600;color:#e2e8f0;">Planta de Estacas Internas &amp; Transporte Refrigerado</div>
        <ul style="margin:6px 0 0;padding-left:18px;font-size:12px;color:#cbd5e1;">
          ${dowelRows}
          <li>Transporte Frio: <strong>${escapeHtml(cold.refrigerated_van_target_temp_c)}</strong> · Força-G máx: ${cold.max_safe_cornering_g_force} g</li>
        </ul>
      </div>
      <div class="tile">
        <div style="font-size:12px;font-weight:600;color:#e2e8f0;">Especificação Studio Render (ControlNet Depth ${data.comfyui_controlnet_render.controlnet_depth_strength} · ${escapeHtml(data.comfyui_controlnet_render.z_depth_cas_uri)})</div>
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

async function runSemanticRecipeSearch() {
  const q = document.getElementById('recipe-search-inp').value || '';
  const box = document.getElementById('recipe-search-results');
  box.textContent = 'A pesquisar combinações seguras (Zero ChromaDB · Reg. UE 1169/2011)...';
  try {
    const r = await fetch('/api/bake/search-recipes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: q, limit: 3 })
    });
    const d = await r.json();
    if (!r.ok || !d.ok) throw new Error(d.error || 'Falha na pesquisa');
    if (!d.matches || !d.matches.length) {
      box.textContent = 'Nenhuma receita cumpre todas as restrições indicadas.';
      return;
    }
    window.__bakeSearchMatches = d.matches;
    box.innerHTML = d.matches.map((m, idx) => `
      <div style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;gap:6px;">
        <span><strong>${escapeHtml(m.sponge_name)}</strong> + ${escapeHtml(m.filling_name)} (${m.wedding_portions} fatias · €${m.total_gross_eur.toFixed(2)})</span>
        <button type="button" class="secondary" style="padding:4px 8px;font-size:11px;" onclick="applySearchedDesign(${idx})">Aplicar</button>
      </div>
    `).join('');
  } catch (e) {
    box.textContent = 'Erro na pesquisa: ' + e.message;
  }
}

function applySearchedDesign(idx) {
  const m = (window.__bakeSearchMatches || [])[idx];
  if (!m) return;
  const dp = m.design_payload;
  document.getElementById('shape-sel').value = dp.shape;
  document.getElementById('sponge-sel').value = dp.sponge_key;
  document.getElementById('filling-sel').value = dp.filling_key;
  document.getElementById('frosting-sel').value = dp.frosting_key;
  tiersState = dp.tiers.map(t => ({ diameter_cm: t.diameter_cm, height_cm: t.height_cm, sponge_key: '', filling_key: '' }));
  renderTiersEditor();
  recalcCake();
}

async function enqueueAsyncComfyRender() {
  const fb = document.getElementById('bridge-feedback');
  const cancelBtn = document.getElementById('btn-render-cancel');
  fb.style.color = '#7dd3fc';
  fb.textContent = 'A agendar tarefa assíncrona ControlNet Depth (RULE-10)...';
  try {
    const payload = Object.assign({}, collectCakePayload(), { simulate_delay_ms: 180 });
    const r = await fetch('/api/bake/render-jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const d = await r.json();
    if (!r.ok || !d.ok) throw new Error(d.error || 'Falha ao criar render job');
    activeRenderJobId = d.job.job_id;
    cancelBtn.classList.remove('hidden');
    for (let i = 0; i < 15; i++) {
      await new Promise(res => setTimeout(res, 120));
      const jr = await fetch('/api/bake/render-jobs/' + encodeURIComponent(activeRenderJobId));
      const jd = await jr.json();
      if (!jd.ok) break;
      fb.textContent = `[${jd.job.progress_pct}%] ${jd.job.stage_pt}`;
      if (jd.job.status === 'COMPLETED' || jd.job.status === 'ABORTED') {
        fb.style.color = jd.job.status === 'COMPLETED' ? '#6ee7b7' : '#fda4af';
        break;
      }
    }
  } catch (e) {
    fb.style.color = '#fda4af';
    fb.textContent = 'Erro Render Job: ' + e.message;
  } finally {
    cancelBtn.classList.add('hidden');
  }
}

async function cancelActiveRenderJob() {
  if (!activeRenderJobId) return;
  await fetch('/api/bake/render-jobs/' + encodeURIComponent(activeRenderJobId) + '/cancel', { method: 'POST' });
}

async function generateDepositMultibanco() {
  const fb = document.getElementById('bridge-feedback');
  fb.style.color = '#fde047';
  fb.textContent = 'A emitir Referência Multibanco Sinal 50% + Fatura SAF-T (PT) v1.04_01...';
  try {
    const payload = Object.assign({}, collectCakePayload(), { payment_method: 'MULTIBANCO' });
    const [rDep, rSaft] = await Promise.all([
      fetch('/api/bake/deposit-checkout', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
      fetch('/api/bake/saft-pt-preview', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    ]);
    const dep = await rDep.json();
    const saft = await rSaft.json();
    if (!dep.ok || !saft.ok) throw new Error(dep.error || saft.error || 'Erro fiscal');
    fb.style.color = '#6ee7b7';
    fb.textContent = `✓ Sinal 50% (€${dep.payment.deposit_amount_eur.toFixed(2)}) · Entidade ${dep.payment.multibanco_entity} · Ref ${dep.payment.multibanco_reference} · SAF-T ${saft.invoice_no} (${saft.atcud})`;
    announce(fb.textContent);
  } catch (e) {
    fb.style.color = '#fda4af';
    fb.textContent = 'Erro fiscal: ' + e.message;
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

async function downloadBakeAsaePdf() {
  const fb = document.getElementById('bridge-feedback');
  fb.style.color = '#a5b4fc';
  fb.textContent = 'A gerar PDF A4 Oficial ASAE (MOD-FT-ASAE-DGAV-ACIP-v2.0)...';
  try {
    const r = await fetch('/api/bake/ficha-asae/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(collectCakePayload())
    });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank', 'noopener');
    fb.style.color = '#6ee7b7';
    fb.textContent = '✓ PDF A4 Oficial ASAE gerado e guardado em pipeline_data/fichas_tecnicas_asae/.';
    announce('PDF A4 ASAE gerado com sucesso.');
  } catch (e) {
    fb.style.color = '#fda4af';
    fb.textContent = 'Erro ao gerar PDF A4 ASAE: ' + e.message;
  }
}

function openFermentationASAE(isPdf) {
  const qs = new URLSearchParams({
    action: 'fermentation',
    flour_mass_g: String(document.getElementById('ferm-flour').value || 5000),
    dough_temp_c: String(document.getElementById('ferm-temp').value || 26),
    hydration_pct: String(document.getElementById('ferm-hyd').value || 72),
    starter_pct: String(document.getElementById('ferm-starter').value || 20)
  });
  const base = isPdf ? '/api/bake/ficha-asae/pdf?' : '/api/bake/ficha-asae/print?';
  window.open(base + qs.toString(), '_blank', 'noopener');
}

async function loadEstablishmentBake() {
  try {
    const r = await fetch('/api/bake/estabelecimento');
    const d = await r.json();
    if (!r.ok || !d.establishment) return;
    const e = d.establishment;
    document.getElementById('estab-denom').value = e.denominacao_social || '';
    document.getElementById('estab-nome').value = e.nome_comercial || '';
    document.getElementById('estab-nif').value = e.nif || '';
    document.getElementById('estab-cae').value = e.cae_principal || '';
    document.getElementById('estab-morada').value = e.morada_estabelecimento || '';
    document.getElementById('estab-licenca').value = e.licenca_rjacsr_dgav || '';
    document.getElementById('estab-haccp').value = e.responsavel_haccp || '';
    document.getElementById('estab-contacto').value = e.contacto_alergenios || '';
  } catch (_) {}
}

async function saveEstablishmentBake() {
  const fb = document.getElementById('estab-feedback');
  fb.style.color = '#a5b4fc';
  fb.textContent = 'A validar NIF Módulo-11 e a carimbar dossier ASAE...';
  try {
    const r = await fetch('/api/bake/estabelecimento', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        denominacao_social: document.getElementById('estab-denom').value,
        nome_comercial: document.getElementById('estab-nome').value,
        nif: document.getElementById('estab-nif').value,
        cae_principal: document.getElementById('estab-cae').value,
        morada_estabelecimento: document.getElementById('estab-morada').value,
        licenca_rjacsr_dgav: document.getElementById('estab-licenca').value,
        responsavel_haccp: document.getElementById('estab-haccp').value,
        contacto_alergenios: document.getElementById('estab-contacto').value
      })
    });
    const d = await r.json();
    if (!r.ok || !d.ok) throw new Error(d.error || d.detail || ('HTTP ' + r.status));
    fb.style.color = '#6ee7b7';
    fb.textContent = `✓ Estabelecimento validado (${d.establishment.denominacao_social} · NIF ${d.establishment.nif}). Todas as Fichas A4 & PDFs atualizados.`;
    announce('Identificação oficial do estabelecimento guardada.');
  } catch (e) {
    fb.style.color = '#fda4af';
    fb.textContent = 'Erro de validação: ' + e.message;
    announce('Erro ao guardar estabelecimento: ' + e.message);
  }
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
      : `✓ Pacote 24h & PDF A4 ASAE (${d.asae_ficha_id}) sincronizados no Dossier!`;
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
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;">
        <button type="button" class="secondary" onclick="openFermentationASAE(false)">🖨️ Ficha Técnica ASAE A4 ↗</button>
        <button type="button" class="secondary" style="border-color:#059669;color:#6ee7b7;" onclick="openFermentationASAE(true)">⬇️ PDF A4 ASAE (Levain)</button>
      </div>
    `;
  } catch (e) {
    out.innerHTML = `<span style="color:#fda4af;">Erro: ${escapeHtml(e.message)}</span> <button type="button" class="secondary" onclick="calcFermentation()">↻ Retry</button>`;
  }
}

async function createClientQuotePortal() {
  const fb = document.getElementById('bridge-feedback');
  try {
    const r = await fetch('/api/bake/quotes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(collectCakePayload())
    });
    const d = await r.json();
    if (!r.ok || !d.ok) throw new Error(d.error || 'Erro ao criar proposta');
    fb.style.color = '#f9a8d4';
    fb.textContent = `✓ Portal Proposta criado: ${d.quote.share_path} · Total €${d.quote.total_gross_eur.toFixed(2)} (Sinal €${d.quote.net_deposit_due_eur.toFixed(2)})`;
  } catch (e) {
    fb.style.color = '#fda4af';
    fb.textContent = 'Erro: ' + e.message;
  }
}

async function dispatchFleetColdChain() {
  const fb = document.getElementById('bridge-feedback');
  try {
    const r = await fetch('/api/bake/fleet-dispatch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...collectCakePayload(), vehicle_plate: 'AA-42-BB', van_temp_c: 3.2, max_expected_lateral_g: 0.22 })
    });
    const d = await r.json();
    if (!r.ok || !d.ok) throw new Error(d.error || 'Erro Frota');
    fb.style.color = '#5eead4';
    fb.textContent = `✓ Frota Refrigerada ${d.delivery.delivery_id} (${d.delivery.at_guia_transporte_doc_code_id}) · Janela Exposição: ${d.delivery.melt_countdown.minutes_until_structural_softening} min`;
  } catch (e) {
    fb.style.color = '#fda4af';
    fb.textContent = 'Erro Frota: ' + e.message;
  }
}

async function downloadCateringCuttingPdf() {
  const fb = document.getElementById('bridge-feedback');
  fb.textContent = 'A gerar PDF Guia de Corte para Catering & Extração de Cavilhas…';
  try {
    const r = await fetch('/api/bake/catering-cutting-guide/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...collectCakePayload(), cake_cutting_time_hhmm: '22:30', drive_minutes_to_venue: 45 })
    });
    if (!r.ok) throw new Error('Falha ao gerar PDF Guia de Corte');
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank', 'noopener');
    fb.style.color = '#fdba74';
    fb.textContent = '✓ PDF Guia de Corte & Controlo de Cavilhas pronto para a equipa de sala.';
  } catch (e) {
    fb.style.color = '#fda4af';
    fb.textContent = 'Erro Guia Corte: ' + e.message;
  }
}

async function runDietarySafeReformulation() {
  const fb = document.getElementById('bridge-feedback');
  fb.textContent = 'A validar reformulação Sem Glúten (<=20 ppm Reg. UE 828/2014) & Sem Lactose…';
  try {
    const r = await fetch('/api/bake/dietary-reformulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...collectCakePayload(), dietary_modes: ['GLUTEN_FREE_APC_20PPM', 'LACTOSE_FREE'] })
    });
    const d = await r.json();
    if (!r.ok || !d.ok) throw new Error(d.error || 'Erro na reformulação');
    fb.style.color = '#d8b4fe';
    fb.textContent = `✓ Reformulação segura validada (H/D=${d.structural_slenderness_verified.h_over_d_ratio}) · Eliminados: ${d.eliminated_allergen_codes.join(', ')}`;
  } catch (e) {
    fb.style.color = '#fda4af';
    fb.textContent = 'Alerta Estrutural / Dietético: ' + e.message;
  }
}

renderTiersEditor();
recalcCake();
</script>
</body>
</html>"""


def create_insight_bake_router(storage_dir: Optional[Path] = None) -> APIRouter:
    engine = InsightBakeEngine(storage_dir=storage_dir)
    router = APIRouter(tags=["InsightBake"])

    @router.get("/status")
    def get_status() -> Dict[str, Any]:
        return engine.get_status()

    @router.get("/estabelecimento")
    def get_establishment() -> Dict[str, Any]:
        return engine.get_establishment_profile()

    @router.put("/estabelecimento")
    def update_establishment(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        try:
            updates = {k: v for k, v in (payload or {}).items() if v is not None}
            return JSONResponse(status_code=200, content=engine.update_establishment_profile(updates))
        except ValueError as exc:
            return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})

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

    def _build_query_payload(
        action: str,
        shape: str,
        sponge_key: str,
        filling_key: str,
        frosting_key: str,
        topper_text: str,
        consumption_mode: str,
        flour_mass_g: float,
        dough_temp_c: float,
        hydration_pct: float,
        starter_pct: float,
    ) -> Dict[str, Any]:
        if action.strip().lower() in ("fermentation", "arrhenius", "sourdough"):
            return {
                "action": "fermentation",
                "flour_mass_g": flour_mass_g,
                "dough_temp_c": dough_temp_c,
                "hydration_pct": hydration_pct,
                "starter_pct": starter_pct,
            }
        return {
            "shape": shape,
            "sponge_key": sponge_key,
            "filling_key": filling_key,
            "frosting_key": frosting_key,
            "topper_text": topper_text,
            "consumption_mode": consumption_mode,
        }

    @router.get("/ficha-asae/print", response_class=HTMLResponse)
    def print_cake_asae_ficha(
        action: str = Query(default="cake"),
        shape: str = Query(default="ROUND"),
        sponge_key: str = Query(default="red_velvet"),
        filling_key: str = Query(default="brigadeiro_gourmet"),
        frosting_key: str = Query(default="swiss_meringue_buttercream"),
        topper_text: str = Query(default="Sofia & Miguel"),
        consumption_mode: str = Query(default="RESTAURACAO_13"),
        flour_mass_g: float = Query(default=5000.0),
        dough_temp_c: float = Query(default=26.0),
        hydration_pct: float = Query(default=72.0),
        starter_pct: float = Query(default=20.0),
    ) -> HTMLResponse:
        q_payload = _build_query_payload(
            action, shape, sponge_key, filling_key, frosting_key,
            topper_text, consumption_mode, flour_mass_g, dough_temp_c, hydration_pct, starter_pct,
        )
        res = engine.execute(q_payload)
        if not res.get("ok"):
            return HTMLResponse(status_code=400, content=f"<h1>Erro Estrutural: {res.get('error')}</h1>")
        qs = urllib.parse.urlencode({k: str(v) for k, v in q_payload.items()})
        est = engine.get_establishment_profile()["establishment"]
        return HTMLResponse(
            content=render_cake_asae_ficha_html(
                res,
                establishment=est,
                pdf_download_url=f"/api/bake/ficha-asae/pdf?{qs}",
            )
        )

    @router.get("/ficha-asae/pdf")
    def download_cake_asae_ficha_pdf_get(
        action: str = Query(default="cake"),
        shape: str = Query(default="ROUND"),
        sponge_key: str = Query(default="red_velvet"),
        filling_key: str = Query(default="brigadeiro_gourmet"),
        frosting_key: str = Query(default="swiss_meringue_buttercream"),
        topper_text: str = Query(default="Sofia & Miguel"),
        consumption_mode: str = Query(default="RESTAURACAO_13"),
        flour_mass_g: float = Query(default=5000.0),
        dough_temp_c: float = Query(default=26.0),
        hydration_pct: float = Query(default=72.0),
        starter_pct: float = Query(default=20.0),
    ) -> Response:
        q_payload = _build_query_payload(
            action, shape, sponge_key, filling_key, frosting_key,
            topper_text, consumption_mode, flour_mass_g, dough_temp_c, hydration_pct, starter_pct,
        )
        bundle = engine.export_asae_ficha_artifacts(q_payload)
        if not bundle.get("ok"):
            return JSONResponse(status_code=400, content=bundle)
        ficha = bundle["ficha"]
        return Response(
            content=bundle["pdf_bytes"],
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{ficha.ficha_id}.pdf"',
                "Cache-Control": "no-store",
            },
        )

    @router.post("/ficha-asae/pdf")
    def download_cake_asae_ficha_pdf_post(payload: Dict[str, Any] = Body(default={})) -> Response:
        bundle = engine.export_asae_ficha_artifacts(payload or {})
        if not bundle.get("ok"):
            return JSONResponse(status_code=400, content=bundle)
        ficha = bundle["ficha"]
        return Response(
            content=bundle["pdf_bytes"],
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{ficha.ficha_id}.pdf"',
                "Cache-Control": "no-store",
            },
        )

    @router.get("/fichas-tecnicas/caderno-alergenios.pdf")
    def download_bake_counter_allergen_matrix_pdf() -> Response:
        pdf_bytes = engine.render_counter_allergen_matrix_pdf()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'inline; filename="Quadro_Alergenios_Balcao_ASAE_DL26_2016.pdf"',
                "Cache-Control": "no-store",
            },
        )

    @router.post("/reserve-fresco")
    @router.post("/reserve-pastelaria")
    def reserve_custom_cake_in_pastelaria(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.dispatch_custom_cake_to_pastelaria(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/deposit-checkout")
    def create_deposit_checkout(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.create_deposit_payment_intent(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/deposit-confirm")
    def confirm_deposit_checkout(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.confirm_deposit_payment(
            payment_id=str((payload or {}).get("payment_id") or ""),
            transaction_ref=str((payload or {}).get("transaction_ref") or "SIBS-ACK-OK"),
        )
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/saft-pt-preview")
    @router.post("/fiscal/saft-xml")
    def export_saft_pt_preview(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.export_saft_pt_invoice_xml(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/render-jobs")
    def submit_async_render_job(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.submit_comfyui_render_job(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.get("/render-jobs/{job_id}")
    def get_async_render_job(job_id: str) -> JSONResponse:
        res = engine.get_comfyui_render_job(job_id)
        return JSONResponse(status_code=200 if res.get("ok") else 404, content=res)

    @router.post("/render-jobs/{job_id}/cancel")
    def cancel_async_render_job(job_id: str) -> JSONResponse:
        res = engine.cancel_comfyui_render_job(job_id)
        return JSONResponse(status_code=200 if res.get("ok") else 404, content=res)

    @router.post("/search-recipes")
    def search_safe_recipes(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        data = payload or {}
        res = engine.search_safe_cake_configurations(
            query=str(data.get("query") or ""),
            exclude_allergens=data.get("exclude_allergens"),
            min_portions=int(data.get("min_portions", 30)),
            ambient_temp_c=float(data.get("ambient_temp_c", 21.0)),
            limit=int(data.get("limit", 5)),
        )
        return JSONResponse(status_code=200, content=res)

    @router.post("/solve-budget")
    def solve_cake_by_guests_budget(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        data = payload or {}
        res = engine.solve_cake_by_guests_and_budget(
            guest_count=int(data.get("guest_count", 60)),
            max_budget_eur=float(data.get("max_budget_eur", 280.0)),
            exclude_allergens=data.get("exclude_allergens"),
            venue_temp_c=float(data.get("venue_temp_c", 22.0)),
            preferred_shape=str(data.get("preferred_shape") or "ROUND"),
            consumption_mode=str(data.get("consumption_mode") or "RESTAURACAO_13"),
        )
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/tasting-box")
    def book_tasting_box(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.create_tasting_box_order(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/quotes")
    def create_client_quote(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.create_shareable_client_quote(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.get("/quotes/{quote_token}")
    def get_client_quote(quote_token: str) -> JSONResponse:
        res = engine.get_shareable_client_quote(quote_token)
        return JSONResponse(status_code=200 if res.get("ok") else 404, content=res)

    @router.post("/quotes/{quote_token}/approve")
    def approve_client_quote(quote_token: str, payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        data = payload or {}
        res = engine.approve_shareable_client_quote(
            quote_token=quote_token,
            client_signature_name=str(data.get("client_signature_name") or ""),
            tasting_voucher_code=data.get("tasting_voucher_code"),
            sync_to_pastelaria_kds=bool(data.get("sync_to_pastelaria_kds", True)),
        )
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/catering-timeline")
    def build_catering_timeline_and_cutting_plan(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.compute_venue_assembly_timeline_and_cutting_plan(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/catering-cutting-guide/pdf")
    def download_catering_cutting_guide_pdf(payload: Dict[str, Any] = Body(default={})) -> Response:
        try:
            pdf_bytes = engine.render_catering_cutting_guide_pdf_bytes(payload)
        except ValueError as exc:
            return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'inline; filename="Guia_Corte_Catering_Cavilhas_InsightBake.pdf"',
                "Cache-Control": "no-store",
            },
        )

    @router.post("/stand-rentals")
    def create_stand_rental(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        data = payload or {}
        res = engine.create_stand_rental_deposit(
            stand_code=str(data.get("stand_code") or "SUP-ACRIL-GOLD-01"),
            stand_description=str(data.get("stand_description") or "Pedestal Acrílico & Latão Dourado"),
            deposit_eur=float(data.get("deposit_eur", 80.0)),
            expected_return_date=str(data.get("expected_return_date") or "2026-12-01"),
            quote_token=data.get("quote_token"),
        )
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/stand-rentals/{rental_id}/settle")
    def settle_stand_rental(rental_id: str, payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        data = payload or {}
        res = engine.settle_stand_rental_return(
            rental_id=rental_id,
            returned_intact=bool(data.get("returned_intact", True)),
            damage_fee_eur=float(data.get("damage_fee_eur", 0.0)),
        )
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/dietary-reformulate")
    def reformulate_dietary_cake(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.reformulate_dietary_safe_cake(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.get("/fiscal/locales")
    def get_bake_fiscal_locales() -> Dict[str, Any]:
        return engine.get_supported_fiscal_locales()

    @router.post("/fiscal/config")
    def post_bake_fiscal_config(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.configure_locale_fiscal_regime(payload or {})
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/fiscal/cliff-check")
    def post_bake_fiscal_cliff_check(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.check_turnover_cliff_for_quote(payload or {})
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/fiscal/simulate-regime")
    def post_bake_fiscal_simulate_regime(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.simulate_regime_breakeven(payload or {})
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/fleet-dispatch")
    def dispatch_fleet_delivery(payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        res = engine.dispatch_refrigerated_fleet_delivery(payload)
        return JSONResponse(status_code=200 if res.get("ok") else 400, content=res)

    @router.post("/fleet-dispatch/{delivery_id}/pod")
    def confirm_fleet_pod(delivery_id: str, payload: Dict[str, Any] = Body(default={})) -> JSONResponse:
        data = payload or {}
        res = engine.confirm_fleet_proof_of_delivery(
            delivery_id=delivery_id,
            handoff_probe_temp_c=float(data.get("handoff_probe_temp_c", 3.6)),
            pod_photo_cas_uri=str(data.get("pod_photo_cas_uri") or ""),
            receiver_name=str(data.get("receiver_name") or "Responsável Evento"),
        )
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


def mount_insight_bake_plugin(
    app: FastAPI,
    prefix: str = "/api/bake",
    storage_dir: Optional[Path] = None,
) -> bool:
    app.include_router(create_insight_bake_router(storage_dir=storage_dir), prefix=prefix)
    return True

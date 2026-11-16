"""
Unit, Unhappy-Path, Arrhenius Q10, ASAE Ficha & Cross-Workspace Bridge Regression Tests
for `CulinaForma™` (`culina_forma` / `:4030 /api/culinaforma`, backward-compatible `insight_bake` / `/api/bake`).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from culina_forma import CulinaFormaEngine
from culina_forma.server import app as culina_app
from insight_bake.engine import InsightBakeEngine, validate_portuguese_nif_modulo11
from insight_bake.server import app


class TestInsightBake(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = CulinaFormaEngine()
        self.client = TestClient(app)

    def test_01_health_status_3d_studio_and_widget_js(self) -> None:
        r_health = self.client.get("/health")
        self.assertEqual(r_health.status_code, 200)
        self.assertEqual(r_health.json()["service"], "CulinaForma")
        self.assertEqual(r_health.json()["legacy_alias"], "InsightBake")
        self.assertEqual(r_health.json()["api_prefix"], "/api/culinaforma")
        self.assertEqual(r_health.json()["legacy_api_prefix"], "/api/bake")
        self.assertEqual(r_health.json()["port"], 4030)

        for status_route in ("/api/culinaforma/status", "/api/bake/status"):
            r_status = self.client.get(status_route)
            self.assertEqual(r_status.status_code, 200)
            st = r_status.json()
            self.assertTrue(st["ok"])
            self.assertEqual(st["member_id"], "CulinaForma")
            self.assertEqual(st["product"], "CulinaForma")
            self.assertEqual(st["eu_14_allergens_supported"], 14)
            self.assertIn("HEART", st["available_shapes"])

        for studio_route in ("/api/culinaforma/studio", "/api/bake/studio"):
            r_studio = self.client.get(studio_route)
            self.assertEqual(r_studio.status_code, 200)
            self.assertIn("CulinaForma™", r_studio.text)
            self.assertNotIn("radial-gradient", r_studio.text)

        r_widget = self.client.get("/api/culinaforma/widget.js")
        self.assertEqual(r_widget.status_code, 200)
        self.assertIn("customElements.define('culina-forma'", r_widget.text)
        self.assertIn("customElements.define('insight-bake'", r_widget.text)

    def test_02_design_3d_shapes_heart_vs_round_allergens_and_iva_regimes(self) -> None:
        r_heart = self.client.post(
            "/api/bake/design",
            json={
                "shape": "HEART",
                "tiers": [
                    {"diameter_cm": 30.0, "height_cm": 12.0},
                    {"diameter_cm": 22.0, "height_cm": 12.0},
                    {"diameter_cm": 15.0, "height_cm": 14.0},
                ],
                "sponge_key": "nozes_vinho_porto",
                "filling_key": "pistacio_tahini_crocante",
                "frosting_key": "ganache_blindagem_fondant",
                "consumption_mode": "TAKEAWAY_23",
                "client_nif": "509442013",
                "topper_text": "Inês & João",
            },
        )
        self.assertEqual(r_heart.status_code, 200)
        body = r_heart.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["threejs_3d_scene"]["shape"], "HEART")
        self.assertEqual(body["threejs_3d_scene"]["tiers"][0]["geometry_type"], "ExtrudeHeartGeometry")
        self.assertEqual(body["threejs_3d_scene"]["total_height_cm"], 38.0)
        self.assertEqual(len(body["portions_and_structure"]["tier_dowel_blueprint"]), 2)

        codes = set(body["allergens_eu_1169_2011"]["allergen_codes"])
        self.assertTrue({"GLUTEN", "EGGS", "SOY", "MILK", "NUTS", "SESAME", "SULPHITES"}.issubset(codes))
        self.assertEqual(body["pricing_and_at_invoicing"]["iva_rate_pct"], 23.0)
        self.assertTrue(body["pricing_and_at_invoicing"]["atcud_preview"].startswith("ATCUD:"))
        self.assertEqual(body["comfyui_controlnet_render"]["controlnet_depth_strength"], 0.88)

        # Verify Modulo-11 Portuguese NIF validator directly
        self.assertTrue(validate_portuguese_nif_modulo11("501964843"))
        self.assertFalse(validate_portuguese_nif_modulo11("501964840"))

    def test_03_arrhenius_q10_fermentation_and_web_component_contract(self) -> None:
        # Direct Web Component payload compatibility (`flour_mass_g` + `dough_temp_c` on `/api/bake/execute`)
        r_warm = self.client.post(
            "/api/bake/execute",
            json={"flour_mass_g": 5000, "dough_temp_c": 28.0, "hydration_pct": 75.0, "point_in_time": "2026-04-20"},
        )
        r_cool = self.client.post(
            "/api/bake/fermentation",
            json={"flour_mass_g": 5000, "dough_temp_c": 20.0, "hydration_pct": 75.0},
        )
        self.assertEqual(r_warm.status_code, 200)
        self.assertEqual(r_cool.status_code, 200)
        w_body = r_warm.json()
        c_body = r_cool.json()
        self.assertEqual(w_body["mode"], "arrhenius_fermentation_and_bakers_pct")
        self.assertLess(
            w_body["arrhenius_fermentation_kinetics"]["estimated_bulk_fermentation_hours"],
            c_body["arrhenius_fermentation_kinetics"]["estimated_bulk_fermentation_hours"],
        )
        self.assertEqual(w_body["bakers_percentage_bom_grams"]["water_g"], 3750.0)

        # Unhappy path: thermal yeast inactivation (>42C) rejected
        r_bad_temp = self.client.post("/api/bake/fermentation", json={"flour_mass_g": 1000, "dough_temp_c": 55.0})
        self.assertEqual(r_bad_temp.status_code, 400)
        self.assertIn("UNSAFE_DOUGH_TEMP_C", r_bad_temp.json()["error"])

    def test_04_printable_asae_ficha_and_pastelaria_bridge(self) -> None:
        r_ficha = self.client.get(
            "/api/bake/ficha-asae/print?shape=HEXAGON&sponge_key=chocolate_belga_70&topper_text=Casamento"
        )
        self.assertEqual(r_ficha.status_code, 200)
        self.assertIn("FICHA TÉCNICA DE FABRICO PRÓPRIO", r_ficha.text)
        self.assertIn("FT-ASAE-BAKE-", r_ficha.text)

        r_bridge = self.client.post(
            "/api/bake/reserve-pastelaria",
            json={"shape": "ROUND", "topper_text": "Sofia & Miguel", "client_name": "Sofia"},
        )
        self.assertEqual(r_bridge.status_code, 200)
        self.assertTrue(r_bridge.json()["ok"])
        self.assertIn(r_bridge.json()["bridge_mode"], ("LIVE_HTTP_4029", "QUEUED_HANDOFF_PACKET"))

    def test_05_unhappy_path_inverted_tier_slenderness_binary_blob_and_pii_scrub(self) -> None:
        # 1. Unstable inverted tier (30cm stacked on top of 15cm) rejected
        r_inv = self.client.post(
            "/api/bake/design",
            json={"tiers": [{"diameter_cm": 15.0, "height_cm": 12.0}, {"diameter_cm": 30.0, "height_cm": 12.0}]},
        )
        self.assertEqual(r_inv.status_code, 400)
        self.assertIn("INVERTED_UNSTABLE_TIER", r_inv.json()["error"])

        # 2. Excessive slenderness ratio (total height / base diameter > 2.6) rejected
        r_tall = self.client.post(
            "/api/bake/design",
            json={"tiers": [{"diameter_cm": 10.0, "height_cm": 28.0}]},
        )
        self.assertEqual(r_tall.status_code, 400)
        self.assertIn("SLENDERNESS_RATIO_UNSAFE", r_tall.json()["error"])

        # 3. Binary blob rejected
        bad_blob = self.engine.execute({"raw_blob": "data:image/png;base64," + ("A" * 600)})
        self.assertFalse(bad_blob["ok"])
        self.assertEqual(bad_blob["error"], "BINARY_BLOB_REJECTED_USE_CAS_URI")

        # 4. PII scrubbed
        r_scrub = self.client.post("/api/bake/scrub", json={"text": "Cliente NIF 123456789"})
        self.assertEqual(r_scrub.status_code, 200)
        self.assertNotIn("123456789", r_scrub.json()["scrubbed_text"])

    def test_06_native_vector_asae_pdf_arrhenius_pdf_matrix_and_establishment(self) -> None:
        import tempfile
        from io import BytesIO
        from fastapi import FastAPI
        from pypdf import PdfReader
        from insight_bake.router import mount_insight_bake_plugin

        with tempfile.TemporaryDirectory() as tmp:
            tmp_app = FastAPI()
            mount_insight_bake_plugin(tmp_app, prefix="/api/bake", storage_dir=Path(tmp))
            tmp_client = TestClient(tmp_app)

            # 1. Invalid Modulo-11 NIF rejected (400), valid NIF accepted & stamped
            r_bad_nif = tmp_client.put("/api/bake/estabelecimento", json={"nif": "501964840"})
            self.assertEqual(r_bad_nif.status_code, 400)

            r_est_ok = tmp_client.put(
                "/api/bake/estabelecimento",
                json={
                    "denominacao_social": "Atelier Cake Design Chiado, Lda.",
                    "nome_comercial": "Chiado 3D Cake Atelier",
                    "nif": "501964843",
                    "responsavel_haccp": "Chef Eng.º Duarte Vasconcelos",
                },
            )
            self.assertEqual(r_est_ok.status_code, 200)
            self.assertEqual(r_est_ok.json()["establishment"]["nif"], "501964843")

            # 2. 3D Multi-Tier HEART Cake Vector A4 PDF with 7 Annex II Allergens + Establishment stamp
            r_cake_pdf = tmp_client.post(
                "/api/bake/ficha-asae/pdf",
                json={
                    "shape": "HEART",
                    "tiers": [
                        {"diameter_cm": 28.0, "height_cm": 12.0},
                        {"diameter_cm": 20.0, "height_cm": 12.0},
                    ],
                    "sponge_key": "nozes_vinho_porto",
                    "filling_key": "pistacio_tahini_crocante",
                    "frosting_key": "ganache_blindagem_fondant",
                    "topper_text": "Leonor & Vasco",
                },
            )
            self.assertEqual(r_cake_pdf.status_code, 200)
            self.assertEqual(r_cake_pdf.headers["content-type"], "application/pdf")
            self.assertTrue(r_cake_pdf.content.startswith(b"%PDF-"))
            cake_pdf_txt = "\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(r_cake_pdf.content)).pages)
            self.assertIn("MOD-FT-ASAE-DGAV-ACIP-v2.0", cake_pdf_txt)
            self.assertIn("Atelier Cake Design Chiado, Lda.", cake_pdf_txt)
            self.assertIn("501964843", cake_pdf_txt)
            self.assertIn("Leonor & Vasco", cake_pdf_txt)

            # 3. Arrhenius Q10 Sourdough Fermentation Vector A4 PDF (GET & POST)
            r_ferm_pdf = tmp_client.get(
                "/api/bake/ficha-asae/pdf?action=fermentation&flour_mass_g=5000&dough_temp_c=26&hydration_pct=74&starter_pct=20"
            )
            self.assertEqual(r_ferm_pdf.status_code, 200)
            self.assertTrue(r_ferm_pdf.content.startswith(b"%PDF-"))
            ferm_pdf_txt = "\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(r_ferm_pdf.content)).pages)
            self.assertIn("FT-ASAE-FERM-", ferm_pdf_txt)
            self.assertIn("Levain", ferm_pdf_txt)

            # 4. Horizontal Counter 14-Allergen Matrix PDF (`DL n.º 26/2016`)
            r_mat = tmp_client.get("/api/bake/fichas-tecnicas/caderno-alergenios.pdf")
            self.assertEqual(r_mat.status_code, 200)
            self.assertTrue(r_mat.content.startswith(b"%PDF-"))
            mat_txt = "\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(r_mat.content)).pages)
            self.assertIn("Decreto-Lei n.º 26/2016", mat_txt)
            self.assertIn("Atelier Cake Design Chiado, Lda.", mat_txt)

            # 5. Unhappy path: inverted tier rejected on PDF endpoint with HTTP 400
            r_bad_pdf = tmp_client.post(
                "/api/bake/ficha-asae/pdf",
                json={"tiers": [{"diameter_cm": 12.0, "height_cm": 12.0}, {"diameter_cm": 28.0, "height_cm": 12.0}]},
            )
            self.assertEqual(r_bad_pdf.status_code, 400)

    def test_07_per_tier_flavors_cutaway_and_eu1169_nutrition(self) -> None:
        res = self.client.post(
            "/api/bake/execute",
            json={
                "shape": "ROUND",
                "tiers": [
                    {"diameter_cm": 28.0, "height_cm": 12.0, "sponge_key": "chocolate_belga_70", "filling_key": "brigadeiro_gourmet"},
                    {"diameter_cm": 20.0, "height_cm": 12.0, "sponge_key": "amendoa_sem_gluten", "filling_key": "pistacio_tahini_crocante"},
                ],
                "frosting_key": "swiss_meringue_buttercream",
            },
        )
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body["ok"])
        self.assertTrue(body["threejs_3d_scene"]["mixed_tier_flavors"])
        self.assertTrue(body["threejs_3d_scene"]["cutaway_slice_ready"])
        tiers = body["threejs_3d_scene"]["tiers"]
        self.assertEqual(len(tiers[0]["cutaway_layers"]), 5)
        self.assertEqual(len(body["recipe_bom_grams"]["per_tier_flavors"]), 2)
        alg = set(body["allergens_eu_1169_2011"]["allergen_codes"])
        self.assertTrue({"GLUTEN", "NUTS", "SESAME", "MILK", "EGGS"}.issubset(alg))
        nutr = body["nutritional_declaration_eu_1169"]
        self.assertGreater(nutr["per_100g"]["energy_kcal"], 200.0)
        self.assertGreater(nutr["per_portion"]["energy_kj"], nutr["per_portion"]["energy_kcal"])

    def test_08_mbway_multibanco_deposit_and_saft_pt_xml(self) -> None:
        # 1. Unhappy path: invalid MB WAY phone rejected
        bad_mbw = self.client.post(
            "/api/bake/deposit-checkout",
            json={"payment_method": "MBWAY", "mbway_phone": "12345"},
        )
        self.assertEqual(bad_mbw.status_code, 400)

        # 2. Valid MB WAY & Multibanco Modulo-97 + settlement + double-settle unhappy path
        ok_mbw = self.client.post(
            "/api/bake/deposit-checkout",
            json={"payment_method": "MBWAY", "mbway_phone": "+351 912345678"},
        )
        self.assertEqual(ok_mbw.status_code, 200)
        self.assertIn("***", ok_mbw.json()["payment"]["mbway_phone_masked"])

        ok_mb = self.client.post("/api/bake/deposit-checkout", json={"payment_method": "MULTIBANCO"})
        self.assertEqual(ok_mb.status_code, 200)
        pay = ok_mb.json()["payment"]
        self.assertEqual(pay["multibanco_entity"], "21403")
        self.assertRegex(pay["multibanco_reference"], r"^\d{3} \d{3} \d{3}$")
        pid = pay["payment_id"]

        conf1 = self.client.post("/api/bake/deposit-confirm", json={"payment_id": pid, "transaction_ref": "SIBS-7788"})
        self.assertEqual(conf1.status_code, 200)
        self.assertEqual(conf1.json()["payment"]["status"], "SETTLED_50PCT_DEPOSIT")

        conf2 = self.client.post("/api/bake/deposit-confirm", json={"payment_id": pid})
        self.assertEqual(conf2.status_code, 400)

        # 3. SAF-T (PT) v1.04_01 XML preview + invalid NIF unhappy path
        bad_saft = self.client.post("/api/bake/saft-pt-preview", json={"client_nif": "501964840"})
        self.assertEqual(bad_saft.status_code, 400)

        ok_saft = self.client.post(
            "/api/bake/saft-pt-preview",
            json={"client_nif": "501964843", "consumption_mode": "TAKEAWAY_23"},
        )
        self.assertEqual(ok_saft.status_code, 200)
        saft = ok_saft.json()
        self.assertEqual(saft["saft_pt_version"], "1.04_01")
        self.assertIn("urn:OECD:StandardAuditFile-Tax:PT_1.04_01", saft["xml"])
        self.assertIn("<TaxPercentage>23.00</TaxPercentage>", saft["xml"])

    def test_09_async_comfyui_render_queue_abort_and_semantic_recipe_search(self) -> None:
        import time

        # 1. Unhappy path: non-CAS URI rejected
        bad_uri = self.client.post(
            "/api/bake/render-jobs",
            json={"z_depth_cas_uri": "http://example.com/depth.png"},
        )
        self.assertEqual(bad_uri.status_code, 400)

        # 2. Async render job completes with CAS URI
        r_job = self.client.post("/api/bake/render-jobs", json={"simulate_delay_ms": 15})
        self.assertEqual(r_job.status_code, 200)
        jid = r_job.json()["job"]["job_id"]
        deadline = time.time() + 4.0
        cur = r_job.json()["job"]
        while time.time() < deadline:
            cur = self.client.get(f"/api/bake/render-jobs/{jid}").json()["job"]
            if cur["status"] in ("COMPLETED", "ABORTED"):
                break
            time.sleep(0.03)
        self.assertEqual(cur["status"], "COMPLETED")
        self.assertTrue(cur["output_render_cas_uri"].startswith("cas://culina-forma/renders/"))

        # 3. EU AI Act Art. 14 abortable render job
        r_slow = self.client.post("/api/bake/render-jobs", json={"simulate_delay_ms": 400})
        slow_id = r_slow.json()["job"]["job_id"]
        r_cancel = self.client.post(f"/api/bake/render-jobs/{slow_id}/cancel")
        self.assertEqual(r_cancel.status_code, 200)
        self.assertEqual(r_cancel.json()["job"]["status"], "ABORTED")

        # 4. Semantic & allergen/thermal constraint search (Zero ChromaDB RULE-16)
        r_search = self.client.post(
            "/api/bake/search-recipes",
            json={"query": "casamento sem glúten verão 27C 50 pessoas"},
        )
        self.assertEqual(r_search.status_code, 200)
        sdata = r_search.json()
        self.assertGreaterEqual(sdata["total_matches"], 1)
        for m in sdata["matches"]:
            self.assertNotIn("GLUTEN", m["allergen_codes"])
            self.assertGreaterEqual(m["max_safe_ambient_temp_c"], 27.0)
            self.assertGreaterEqual(m["wedding_portions"], 50)

    def test_10_reverse_guest_budget_solver_tasting_box_voucher_and_client_quote_portal(self) -> None:
        # 1. Unhappy path: impossible budget rejected
        r_imp = self.client.post("/api/bake/solve-budget", json={"guest_count": 120, "max_budget_eur": 35.0})
        self.assertEqual(r_imp.status_code, 400)

        # 2. Reverse solver finds optimal nut-free configuration within guest & EUR bounds
        r_solve = self.client.post(
            "/api/bake/solve-budget",
            json={"guest_count": 45, "max_budget_eur": 360.0, "exclude_allergens": ["NUTS"], "venue_temp_c": 23.0},
        )
        self.assertEqual(r_solve.status_code, 200)
        rec = r_solve.json()["recommended_solution"]
        self.assertGreaterEqual(rec["wedding_portions"], 45)
        self.assertLessEqual(rec["total_gross_eur"], 360.0)
        self.assertNotIn("NUTS", rec["allergen_codes"])

        # 3. Book 4-flavor Caixa de Prova + apply credit on Client Quote Portal + block double-redemption
        r_tb = self.client.post("/api/bake/tasting-box", json={"client_name": "Clara & Diogo", "box_price_eur": 25.0})
        self.assertEqual(r_tb.status_code, 200)
        voucher = r_tb.json()["tasting_box"]["voucher_code"]

        r_qt = self.client.post("/api/bake/quotes", json={"event_title": "Casamento Clara & Diogo"})
        self.assertEqual(r_qt.status_code, 200)
        q_tok = r_qt.json()["quote"]["quote_token"]
        init_dep = r_qt.json()["quote"]["initial_deposit_50pct_eur"]

        r_get_q = self.client.get(f"/api/bake/quotes/{q_tok}")
        self.assertEqual(r_get_q.status_code, 200)

        r_app = self.client.post(
            f"/api/bake/quotes/{q_tok}/approve",
            json={"client_signature_name": "Clara Monteiro", "tasting_voucher_code": voucher},
        )
        self.assertEqual(r_app.status_code, 200)
        approved = r_app.json()["quote"]
        self.assertEqual(approved["status"], "LOCKED_APPROVED")
        self.assertAlmostEqual(approved["net_deposit_due_eur"], round(init_dep - 25.0, 2), places=2)

        # Unhappy path: double quote approval & voucher reuse rejected
        r_app2 = self.client.post(
            f"/api/bake/quotes/{q_tok}/approve",
            json={"client_signature_name": "Clara Monteiro"},
        )
        self.assertEqual(r_app2.status_code, 400)

    def test_11_fleet_cold_chain_gforce_at_guia_transporte_melt_countdown_and_cas_pod(self) -> None:
        # 1. Unhappy paths: excessive G-force (>0.35g) or warm van (>5.0°C) blocked
        r_bad_g = self.client.post(
            "/api/bake/fleet-dispatch",
            json={"vehicle_plate": "AA-42-BB", "van_temp_c": 3.2, "max_expected_lateral_g": 0.52},
        )
        self.assertEqual(r_bad_g.status_code, 400)

        r_bad_t = self.client.post(
            "/api/bake/fleet-dispatch",
            json={"vehicle_plate": "AA-42-BB", "van_temp_c": 8.5, "max_expected_lateral_g": 0.20},
        )
        self.assertEqual(r_bad_t.status_code, 400)

        # 2. Valid cold-chain dispatch with AT Guia de Transporte & summer melt countdown
        r_disp = self.client.post(
            "/api/bake/fleet-dispatch",
            json={"vehicle_plate": "AA-42-BB", "van_temp_c": 3.2, "max_expected_lateral_g": 0.22, "venue_temp_c": 30.0, "venue_rh_pct": 74.0},
        )
        self.assertEqual(r_disp.status_code, 200)
        deliv = r_disp.json()["delivery"]
        did = deliv["delivery_id"]
        self.assertTrue(deliv["at_guia_transporte_doc_code_id"].startswith("AT-"))
        self.assertLess(deliv["melt_countdown"]["minutes_until_structural_softening"], 120)

        # 3. POD requires cas:// URI and handoff probe <= +6.0°C
        r_bad_pod = self.client.post(
            f"/api/bake/fleet-dispatch/{did}/pod",
            json={"handoff_probe_temp_c": 3.8, "pod_photo_cas_uri": "https://not-cas/img.jpg"},
        )
        self.assertEqual(r_bad_pod.status_code, 400)

        r_ok_pod = self.client.post(
            f"/api/bake/fleet-dispatch/{did}/pod",
            json={"handoff_probe_temp_c": 3.8, "pod_photo_cas_uri": "cas://insight-fleet/pod/venue-handoff-01.webp", "receiver_name": "Chefe Sala Quinta"},
        )
        self.assertEqual(r_ok_pod.status_code, 200)
        self.assertEqual(r_ok_pod.json()["delivery"]["status"], "DELIVERED_POD_SIGNED")

    def test_12_catering_cutting_guide_pdf_golden_hour_timeline_and_stand_caucao_ledger(self) -> None:
        from io import BytesIO
        from pypdf import PdfReader

        # Unhappy path: invalid cutting time format
        r_bad_tl = self.client.post("/api/bake/catering-timeline", json={"cake_cutting_time_hhmm": "29:99"})
        self.assertEqual(r_bad_tl.status_code, 400)

        payload = {
            "shape": "ROUND",
            "tiers": [
                {"diameter_cm": 30.0, "height_cm": 12.0},
                {"diameter_cm": 22.0, "height_cm": 12.0},
                {"diameter_cm": 15.0, "height_cm": 14.0},
            ],
            "cake_cutting_time_hhmm": "22:30",
            "drive_minutes_to_venue": 45,
            "venue_temp_c": 26.0,
        }
        r_tl = self.client.post("/api/bake/catering-timeline", json=payload)
        self.assertEqual(r_tl.status_code, 200)
        tl_data = r_tl.json()
        self.assertGreater(tl_data["total_internal_dowels_to_account_for"], 0)
        self.assertEqual(len(tl_data["tier_disassembly_and_cutting_steps"]), 3)

        r_pdf = self.client.post("/api/bake/catering-cutting-guide/pdf", json=payload)
        self.assertEqual(r_pdf.status_code, 200)
        self.assertTrue(r_pdf.content.startswith(b"%PDF-"))
        pdf_txt = "\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(r_pdf.content)).pages)
        self.assertIn("CAVILHAS", pdf_txt)
        self.assertIn("22:30", pdf_txt)

        # Reusable stand security deposit (Caução CIVA Art. 16.º n.º 6): intact 0% IVA vs damaged 23% IVA
        r_c1 = self.client.post("/api/bake/stand-rentals", json={"stand_code": "SUP-GOLD-01", "deposit_eur": 90.0, "expected_return_date": "2026-12-05"})
        self.assertEqual(r_c1.status_code, 200)
        rid1 = r_c1.json()["rental"]["rental_id"]
        r_s1 = self.client.post(f"/api/bake/stand-rentals/{rid1}/settle", json={"returned_intact": True})
        self.assertEqual(r_s1.status_code, 200)
        self.assertEqual(r_s1.json()["rental"]["status"], "REFUNDED_INTACT_0PCT_IVA")
        self.assertEqual(r_s1.json()["rental"]["refunded_eur"], 90.0)

        # Double-settle blocked
        self.assertEqual(self.client.post(f"/api/bake/stand-rentals/{rid1}/settle", json={"returned_intact": True}).status_code, 400)

        # Damaged stand converts withheld deposit to 23% IVA compensation invoice with ATCUD
        r_c2 = self.client.post("/api/bake/stand-rentals", json={"stand_code": "SUP-ACRIL-02", "deposit_eur": 100.0, "expected_return_date": "2026-12-06"})
        rid2 = r_c2.json()["rental"]["rental_id"]
        r_s2 = self.client.post(f"/api/bake/stand-rentals/{rid2}/settle", json={"returned_intact": False, "damage_fee_eur": 61.50})
        self.assertEqual(r_s2.status_code, 200)
        self.assertEqual(r_s2.json()["rental"]["status"], "DAMAGE_INVOICED_23PCT_IVA")
        self.assertEqual(r_s2.json()["rental"]["refunded_eur"], 38.50)
        self.assertTrue(str(r_s2.json()["rental"]["damage_atcud"]).startswith("ATCUD:BAKECAU26-"))

    def test_13_dietary_reformulator_slenderness_guard_and_quote_to_pastelaria_kds_sync(self) -> None:
        # Tall narrow cake passes wheat (H/D = 38/20 = 1.90 <= 2.20), but fails Gluten-Free + Vegan (1.90 > 1.65)
        tall_payload = {
            "shape": "ROUND",
            "tiers": [{"diameter_cm": 20.0, "height_cm": 20.0}, {"diameter_cm": 15.0, "height_cm": 18.0}],
            "dietary_modes": ["GLUTEN_FREE_APC_20PPM", "VEGAN_100PCT"],
        }
        r_tall = self.client.post("/api/bake/dietary-reformulate", json=tall_payload)
        self.assertEqual(r_tall.status_code, 400)
        self.assertIn("DIETARY_SPONGE_SLENDERNESS_EXCEEDED", r_tall.json()["error"])

        # Wider base (H/D = 24/28 = 0.857 <= 1.65) passes Gluten-Free + Vegan and removes GLUTEN, MILK, EGGS
        safe_payload = {
            "shape": "ROUND",
            "tiers": [{"diameter_cm": 28.0, "height_cm": 12.0}, {"diameter_cm": 20.0, "height_cm": 12.0}],
            "sponge_key": "pao_de_lo_tradicional",
            "filling_key": "brigadeiro_gourmet",
            "frosting_key": "swiss_meringue_buttercream",
            "dietary_modes": ["GLUTEN_FREE_APC_20PPM", "VEGAN_100PCT"],
        }
        r_ref = self.client.post("/api/bake/dietary-reformulate", json=safe_payload)
        self.assertEqual(r_ref.status_code, 200)
        ref_data = r_ref.json()
        self.assertEqual(sorted(ref_data["eliminated_allergen_codes"]), ["EGGS", "GLUTEN", "MILK"])
        # Belgian dark chocolate lecithin in brigadeiro_gourmet keeps SOY properly declared
        self.assertEqual(ref_data["remaining_allergen_codes"], ["SOY"])
        self.assertIn(
            "dietary_reinforcement_note",
            ref_data["structural_slenderness_verified"]["upgraded_tier_dowel_blueprint"][0],
        )

        # Approving a quote automatically syncs a 24h production ticket into InsightPastelaria KDS
        r_qt = self.client.post("/api/bake/quotes", json={"event_title": "Casamento Inês & Pedro", "tiers": [{"diameter_cm": 26.0, "height_cm": 12.0}]})
        qtok = r_qt.json()["quote"]["quote_token"]
        r_app = self.client.post(
            f"/api/bake/quotes/{qtok}/approve",
            json={"client_signature_name": "Inês Marques", "sync_to_pastelaria_kds": True},
        )
        self.assertEqual(r_app.status_code, 200)
        kds_sync = r_app.json()["quote"]["pastelaria_kds_sync"]
        self.assertIsNotNone(kds_sync)
        self.assertTrue(kds_sync["synced"])
        self.assertTrue(str(kds_sync["asae_ficha_id"]).startswith("FT-ASAE-BAKE-"))

    def test_14_locale_ready_exempt_invoicing_gross_cmv_cliff_blocker_and_simulator(self) -> None:
        # 1. Supported locales endpoint lists multi-country profiles (PT, FR, DE, GB, BR, US...)
        r_loc = self.client.get("/api/bake/fiscal/locales")
        self.assertEqual(r_loc.status_code, 200)
        codes = {p["country_code"] for p in r_loc.json()["supported_locales"]}
        self.assertTrue({"PT", "ES", "FR", "DE", "IT", "GB", "BR", "US"}.issubset(codes))

        # 2. Unhappy path: invalid tax_regime rejected
        r_bad = self.client.post("/api/bake/fiscal/config", json={"country_code": "DE", "tax_regime": "BOGUS"})
        self.assertEqual(r_bad.status_code, 400)

        # 3. Exempt 3D cake design includes non-recoverable supplier tax inside CMV and charges 0% output tax
        r_std = self.client.post("/api/bake/design", json={"country_code": "DE", "consumption_mode": "RESTAURACAO_13"}).json()
        r_ex = self.client.post("/api/bake/design", json={"country_code": "DE", "consumption_mode": "EXEMPT_SMALL_BUSINESS"}).json()
        self.assertEqual(r_std["pricing_and_at_invoicing"]["iva_rate_pct"], 19.0)
        self.assertEqual(r_ex["pricing_and_at_invoicing"]["iva_rate_pct"], 0.0)
        self.assertEqual(r_ex["pricing_and_at_invoicing"]["tax_exemption_code"], "USTG-19")
        self.assertGreater(r_ex["pricing_and_at_invoicing"]["non_recoverable_input_tax_included_in_cmv_eur"], 0.0)
        self.assertGreater(
            r_ex["pricing_and_at_invoicing"]["raw_ingredients_and_packaging_cost_eur"],
            r_std["pricing_and_at_invoicing"]["raw_ingredients_and_packaging_cost_eur"],
        )

        # 4. SAF-T XML emits <TaxExemptionCode> below cliff and BLOCKS when crossing intra-year hard cliff
        r_saft_ok = self.client.post(
            "/api/bake/fiscal/saft-xml",
            json={"country_code": "BR", "consumption_mode": "EXEMPT_SMALL_BUSINESS", "ytd_turnover_override": 50000.0},
        )
        self.assertEqual(r_saft_ok.status_code, 200)
        self.assertEqual(r_saft_ok.json()["currency_code"], "BRL")
        self.assertIn("<TaxExemptionCode>CRT-4</TaxExemptionCode>", r_saft_ok.json()["xml"])

        r_saft_cliff = self.client.post(
            "/api/bake/fiscal/saft-xml",
            json={"country_code": "PT", "consumption_mode": "EXEMPT_SMALL_BUSINESS", "ytd_turnover_override": 18700.0},
        )
        self.assertEqual(r_saft_cliff.status_code, 400)
        self.assertIn("HARD_TAX_CLIFF_BREACH", r_saft_cliff.json()["error"])

        # 5. Pre-quote cliff guard + Stay-Exempt vs Opt-In Simulator across UK (GBP) & PT (EUR)
        r_cliff_gb = self.client.post(
            "/api/bake/fiscal/cliff-check",
            json={"country_code": "GB", "tax_regime": "EXEMPT_SMALL_BUSINESS", "ytd_domestic_turnover": 75000.0, "proposed_order_amount": 800.0},
        )
        self.assertEqual(r_cliff_gb.status_code, 200)
        self.assertEqual(r_cliff_gb.json()["currency_code"], "GBP")
        self.assertEqual(r_cliff_gb.json()["status"], "APPROACHING_SOFT_THRESHOLD_80PCT")

        r_sim = self.client.post(
            "/api/bake/fiscal/simulate-regime",
            json={"country_code": "FR", "projected_annual_revenue": 42000.0, "b2b_revenue_share_pct": 10.0, "planned_capex_equipment_net": 500.0},
        )
        self.assertEqual(r_sim.status_code, 200)
        self.assertEqual(r_sim.json()["recommendation"], "STAY_EXEMPT")

    def test_15_insight_fresco_bridge_and_status_v1_8_0(self) -> None:
        r_st = self.client.get("/api/culinaforma/status")
        self.assertEqual(r_st.status_code, 200)
        st_json = r_st.json()
        self.assertEqual(st_json["version"], "1.9.0")
        self.assertIn("SetMiddle Insight™ · Fresco", " ".join(st_json["ecosystem_synergy"]))

        r_res = self.client.post(
            "/api/culinaforma/reserve-fresco",
            json={
                "pastelaria_base_url": "http://127.0.0.1:49999",
                "customer_name": "Atelier Fresco Demo",
                "pickup_iso": "2026-12-20T16:00:00Z",
                "shape": "ROUND",
                "tiers": [{"diameter_cm": 20.0, "height_cm": 10.0}],
            },
        )
        self.assertEqual(r_res.status_code, 200)
        res_json = r_res.json()
        self.assertTrue(res_json["ok"])
        self.assertTrue(str(res_json["asae_ficha_id"]).startswith("FT-ASAE-BAKE-"))
        self.assertIn("/api/fresco/reservations/custom-cake", res_json["target_url"])
        self.assertIn("fresco_reservation", res_json)
        self.assertIn("pastelaria_reservation", res_json)
        self.assertTrue(callable(self.engine.dispatch_custom_cake_to_fresco))

        r_qt = self.client.post("/api/bake/quotes", json={"event_title": "Evento Fresco", "tiers": [{"diameter_cm": 22.0, "height_cm": 12.0}]})
        qtok = r_qt.json()["quote"]["quote_token"]
        r_app = self.client.post(
            f"/api/bake/quotes/{qtok}/approve",
            json={"client_signature_name": "Bruno Fresco", "sync_to_pastelaria_kds": True},
        )
        self.assertEqual(r_app.status_code, 200)
        self.assertTrue(r_app.json()["quote"]["fresco_kds_sync"]["synced"])

    def test_16_bake_existing_fichas_whitelabel_docx_and_human_readability_gate(self) -> None:
        import sys as _sys

        fresco_dir = str(Path(__file__).resolve().parent.parent.parent / "InsightPastelaria")
        if fresco_dir not in _sys.path and Path(fresco_dir).exists():
            _sys.path.insert(0, fresco_dir)
        from insight_fresco.word_ficha_template import audit_docx_human_readability_and_whitelabel

        # 1. Export 3D Multi-Tier Cake (ROUND + hex colors) & Gluten-Free HEART Cake & Sourdough Fermentation via /api/bake/ficha-asae/docx
        for payload in (
            {"shape": "ROUND", "sponge_key": "red_velvet", "filling_key": "brigadeiro_gourmet", "topper_text": "Clássico Red Velvet"},
            {"shape": "HEART", "sponge_key": "amendoa_sem_gluten", "filling_key": "curd_limao_frutos_vermelhos", "topper_text": "Amêndoa Sem Glúten"},
            {"action": "fermentation", "flour_mass_g": 5000.0, "dough_temp_c": 26.0, "hydration_pct": 72.0, "starter_pct": 20.0},
        ):
            r_docx = self.client.post("/api/culinaforma/ficha-asae/docx", json=payload)
            self.assertEqual(r_docx.status_code, 200)
            self.assertIn("wordprocessingml.document", r_docx.headers.get("content-type", ""))
            audit = audit_docx_human_readability_and_whitelabel(r_docx.content)
            self.assertTrue(audit["ok"], f"CulinaForma .docx human-readability failure: {audit['issues']}")
            self.assertGreaterEqual(audit["metrics"]["min_font_size_pt"], 8.5)
            self.assertGreaterEqual(audit["metrics"]["min_wcag_contrast_ratio"], 7.5)
            self.assertLessEqual(audit["metrics"]["max_table_width_cm"], audit["metrics"]["printable_width_cm"] + 0.05)

    def test_17_culina_forma_package_parity_and_backward_compatibility(self) -> None:
        self.assertIs(InsightBakeEngine, CulinaFormaEngine)
        self.assertIs(culina_app, app)
        r_cf = self.client.post(
            "/api/culinaforma/design",
            json={"shape": "HEXAGON", "tiers": [{"diameter_cm": 22.0, "height_cm": 12.0}], "topper_text": "CulinaForma"},
        )
        self.assertEqual(r_cf.status_code, 200)
        cf_body = r_cf.json()
        self.assertEqual(cf_body["member"], "CulinaForma")
        self.assertIn("CulinaForma", cf_body["client_brand"])
        self.assertTrue(cf_body["comfyui_controlnet_render"]["z_depth_cas_uri"].startswith("cas://culina-forma/zdepth/"))

        # Unhappy path on canonical /api/culinaforma/design
        r_bad = self.client.post(
            "/api/culinaforma/design",
            json={"tiers": [{"diameter_cm": 14.0, "height_cm": 12.0}, {"diameter_cm": 28.0, "height_cm": 12.0}]},
        )
        self.assertEqual(r_bad.status_code, 400)
        self.assertIn("INVERTED_UNSTABLE_TIER", r_bad.json()["error"])


if __name__ == "__main__":
    unittest.main()

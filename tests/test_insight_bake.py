"""
Unit, Unhappy-Path, Arrhenius Q10, ASAE Ficha & Cross-Workspace Bridge Regression Tests
for `SetMiddle Insight™ · Bake` (`InsightBake` / `insight_bake`).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from insight_bake.engine import InsightBakeEngine, validate_portuguese_nif_modulo11
from insight_bake.server import app


class TestInsightBake(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = InsightBakeEngine()
        self.client = TestClient(app)

    def test_01_health_status_3d_studio_and_widget_js(self) -> None:
        r_health = self.client.get("/health")
        self.assertEqual(r_health.status_code, 200)
        self.assertEqual(r_health.json()["service"], "InsightBake")
        self.assertEqual(r_health.json()["port"], 4030)

        r_status = self.client.get("/api/bake/status")
        self.assertEqual(r_status.status_code, 200)
        st = r_status.json()
        self.assertTrue(st["ok"])
        self.assertEqual(st["eu_14_allergens_supported"], 14)
        self.assertIn("HEART", st["available_shapes"])

        r_studio = self.client.get("/api/bake/studio")
        self.assertEqual(r_studio.status_code, 200)
        self.assertIn("SetMiddle Insight™ · Bake", r_studio.text)
        self.assertNotIn("radial-gradient", r_studio.text)

        r_widget = self.client.get("/api/bake/widget.js")
        self.assertEqual(r_widget.status_code, 200)
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
        self.assertTrue(cur["output_render_cas_uri"].startswith("cas://insight-bake/renders/"))

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


if __name__ == "__main__":
    unittest.main()

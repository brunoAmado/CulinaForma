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


if __name__ == "__main__":
    unittest.main()

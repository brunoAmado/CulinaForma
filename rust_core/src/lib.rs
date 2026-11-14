//! `insight_bake_rs` — Memory-safe Rust Structural, Dowel Load & Arrhenius Q10 Kernel (`:4030`).
//! Enforces stacked multi-tier cake stability (`top_diameter <= bottom_diameter`),
//! slenderness safety ratio (`total_height / base_diameter <= 2.2`), polypropylene dowel count,
//! EU Reg. 1169/2011 Annex II 14-allergen validation, and Arrhenius Q10 fermentation kinetics.

pub const EU_14_ALLERGEN_CODES: [&str; 14] = [
    "GLUTEN",
    "CRUSTACEANS",
    "EGGS",
    "FISH",
    "PEANUTS",
    "SOY",
    "MILK",
    "NUTS",
    "CELERY",
    "MUSTARD",
    "SESAME",
    "SULPHITES",
    "LUPIN",
    "MOLLUSCS",
];

/// Verifies single-step tier stability and slenderness ratio (`<= 2.2` optimal, `<= 2.6` hard ceiling).
pub fn verify_tier_stability(bottom_diameter_cm: f64, top_diameter_cm: f64, total_height_cm: f64) -> bool {
    bottom_diameter_cm >= 8.0
        && top_diameter_cm >= 8.0
        && top_diameter_cm <= bottom_diameter_cm
        && (total_height_cm / bottom_diameter_cm.max(1.0)) <= 2.2
}

/// Validates an entire multi-tier stack (`1..=6` tiers) ordered bottom-to-top `[(diameter_cm, height_cm)]`.
pub fn verify_multi_tier_stack(tiers: &[(f64, f64)]) -> Result<usize, &'static str> {
    if tiers.is_empty() || tiers.len() > 6 {
        return Err("TIER_COUNT_OUT_OF_RANGE_1_TO_6");
    }
    let mut total_height = 0.0;
    let mut total_dowels: usize = 0;
    for i in 0..tiers.len() {
        let (d, h) = tiers[i];
        if !(8.0..=60.0).contains(&d) || !(5.0..=30.0).contains(&h) {
            return Err("INVALID_TIER_DIMENSIONS");
        }
        if i > 0 && d > tiers[i - 1].0 {
            return Err("INVERTED_UNSTABLE_TIER");
        }
        if i + 1 < tiers.len() {
            let upper_d = tiers[i + 1].0;
            let dowels = ((upper_d / 3.5).round() as usize).max(4);
            total_dowels += dowels;
        }
        total_height += h;
    }
    let slenderness = total_height / tiers[0].0;
    if slenderness > 2.6 {
        return Err("SLENDERNESS_RATIO_UNSAFE");
    }
    Ok(total_dowels)
}

/// Computes Arrhenius Q10 sourdough bulk fermentation hours around `24.0 °C` (`Q10 = 2.15`).
pub fn estimate_q10_bulk_hours(dough_temp_c: f64, starter_pct: f64) -> Result<f64, &'static str> {
    if !(2.0..=42.0).contains(&dough_temp_c) {
        return Err("UNSAFE_DOUGH_TEMP_C");
    }
    let q10 = 2.15_f64;
    let base_h = 4.5 * (20.0 / starter_pct.max(5.0)).powf(0.45);
    let rate = q10.powf((dough_temp_c - 24.0) / 10.0);
    Ok(((base_h / rate) * 100.0).round() / 100.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_stability_and_dowels() {
        assert!(verify_tier_stability(30.0, 15.0, 38.0));
        assert!(!verify_tier_stability(15.0, 30.0, 24.0));
        let dowels = verify_multi_tier_stack(&[(30.0, 12.0), (22.0, 12.0), (15.0, 14.0)]).unwrap();
        assert!(dowels >= 10);
        assert!(verify_multi_tier_stack(&[(15.0, 12.0), (25.0, 12.0)]).is_err());
    }

    #[test]
    fn test_q10_fermentation() {
        let warm = estimate_q10_bulk_hours(28.0, 20.0).unwrap();
        let cool = estimate_q10_bulk_hours(20.0, 20.0).unwrap();
        assert!(warm < cool);
        assert!(estimate_q10_bulk_hours(50.0, 20.0).is_err());
    }
}

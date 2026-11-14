// SetMiddle Insight™ · Bake — Rust Structural & Dowel Load CLI (`:4030`)
use insight_bake_rs::{estimate_q10_bulk_hours, verify_multi_tier_stack, verify_tier_stability};

fn main() {
    let stable = verify_tier_stability(30.0, 15.0, 38.0);
    let dowels = verify_multi_tier_stack(&[(30.0, 12.0), (22.0, 12.0), (15.0, 14.0)]).unwrap_or(0);
    let bulk_h = estimate_q10_bulk_hours(26.0, 20.0).unwrap_or(0.0);
    println!(
        "SetMiddle Insight™ · Bake Rust Structural Engine Ready (:4030) | stable={} | dowels={} | bulk_26c={}h",
        stable, dowels, bulk_h
    );
}

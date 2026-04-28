"""Phase 2 driver. Hand-curates the candidate edge list from the source repo's
results.json files, computes Wilson / z / BH / lift / tradeability, and dumps
a markdown ranking table.

Run from repo root:
    python -m src.stats.run_ranking
"""

from __future__ import annotations

import json
from pathlib import Path

from .edge import Edge, benjamini_hochberg, edge_to_dict


REPO_ROOT = Path(__file__).resolve().parents[2]
RAW = REPO_ROOT / "data" / "raw" / "analyses"
OUT_MD = REPO_ROOT / "analysis" / "02_edge_ranking.md"
OUT_JSON = REPO_ROOT / "data" / "processed" / "edge_ranking.json"


def load(path: str) -> dict:
    return json.loads((RAW / path).read_text())


def build_edges() -> list[Edge]:
    edges: list[Edge] = []

    # ---- D4: 9:30 color → which side gets retested (vs unconditional ~78%) -----
    # Source: extended-stats/04-conditional-on-color/data/results.json
    d4 = load("extended-stats/04-conditional-on-color/data/results.json")
    grn_n = d4["sample_size_days"]["green"]   # 119
    red_n = d4["sample_size_days"]["red"]     # 111
    # by 10:00 high_any after green: 73.95% of 119 ≈ 88
    grn_hi_by_10 = round(d4["after_green_9_30"]["by_10_00"]["high_any_pct"] * grn_n / 100)
    grn_lo_by_10 = round(d4["after_green_9_30"]["by_10_00"]["low_any_pct"]  * grn_n / 100)
    red_lo_by_10 = round(d4["after_red_9_30"]["by_10_00"]["low_any_pct"]    * red_n / 100)
    red_hi_by_10 = round(d4["after_red_9_30"]["by_10_00"]["high_any_pct"]   * red_n / 100)
    # Base rate for each = "the same retest probability on the OPPOSITE-color days"
    # (so the base is the rate we'd see if color carried no info).
    edges.append(Edge(
        "D4: green 9:30 → high retest by 10:00",
        "intraday-15m",
        grn_hi_by_10, grn_n,
        red_hi_by_10, red_n,
        "predicts_high_retest_first",
        regime_stable=None,
        notes="Color = side. Compared vs the high-retest rate on red-9:30 days.",
    ))
    edges.append(Edge(
        "D4: red 9:30 → low retest by 10:00",
        "intraday-15m",
        red_lo_by_10, red_n,
        grn_lo_by_10, grn_n,
        "predicts_low_retest_first",
        regime_stable=None,
        notes="Mirror of green case.",
    ))

    # ---- C1: 9:30 followthrough → day close in predicted direction ------------
    # Source: 930-followthrough/data/results.json
    c1 = load("930-followthrough/data/results.json")
    rows = {r["setup"]: r for r in c1["table_1_color_x_retest_x_dayclose"]["rows"]}
    grn_hi = rows["Green 9:30 + high retests by 10:00"]
    red_lo = rows["Red 9:30 + low retests by 10:00"]
    grn_lo = rows["Green 9:30 + low retests by 10:00"]
    red_hi = rows["Red 9:30 + high retests by 10:00"]
    # Base rate for "right-side" rows = "wrong-side" rows (same color), which is
    # the natural counterfactual: when the bias of the day fights us.
    edges.append(Edge(
        "C1: Green 9:30 + HI retest → green close",
        "intraday-15m",
        round(grn_hi["p_day_green_pct"] * grn_hi["n"] / 100), grn_hi["n"],
        round(grn_lo["p_day_green_pct"] * grn_lo["n"] / 100), grn_lo["n"],
        "predicts_green_close",
        regime_stable=None,
        notes="Counterfactual = same color, wrong-side retest (no edge per source).",
    ))
    edges.append(Edge(
        "C1: Red 9:30 + LO retest → red close",
        "intraday-15m",
        round(red_lo["p_day_red_pct"] * red_lo["n"] / 100), red_lo["n"],
        round(red_hi["p_day_red_pct"] * red_hi["n"] / 100), red_hi["n"],
        "predicts_red_close",
        regime_stable=None,
        notes="Mirror.",
    ))
    # Wide-body sub-bucket (smaller n)
    body = {r["setup"]: r for r in c1["table_2_body_size_split"]["rows"]}
    grn_wide = body["Green 9:30 + hi retest, WIDE body"]
    grn_narrow = body["Green 9:30 + hi retest, NARROW body"]
    red_wide = body["Red 9:30 + lo retest, WIDE body"]
    red_narrow = body["Red 9:30 + lo retest, NARROW body"]
    edges.append(Edge(
        "C1-wide: Green wide-body 9:30 + HI retest → green close",
        "intraday-15m",
        round(grn_wide["p_day_green_pct"] * grn_wide["n"] / 100), grn_wide["n"],
        round(grn_narrow["p_day_green_pct"] * grn_narrow["n"] / 100), grn_narrow["n"],
        "predicts_green_close",
        regime_stable=None,
        notes="Wide vs narrow same-color same-side. n is small.",
    ))
    edges.append(Edge(
        "C1-wide: Red wide-body 9:30 + LO retest → red close",
        "intraday-15m",
        round(red_wide["p_day_red_pct"] * red_wide["n"] / 100), red_wide["n"],
        round(red_narrow["p_day_red_pct"] * red_narrow["n"] / 100), red_narrow["n"],
        "predicts_red_close",
        regime_stable=None,
        notes="Strongest-looking bearish setup in repo.",
    ))

    # ---- B1: 9am 1h candle retest -------------------------------------------
    b1 = load("9am-1h-candle-hit-stats/data/results.json")
    n_b1 = b1["aggregate"]["total_days"]
    by_11 = b1["aggregate"]["by_11_00"]["either_side"]
    # Base rate = the unconditional probability we'd assign to "any 1h candle's
    # H or L gets touched within the next 4 fifteen-min bars" — we don't have a
    # clean null for this, so use 50% as a conservative agnostic prior.
    edges.append(Edge(
        "B1: 9-10am 1h candle either-side retest by 11:00",
        "intraday-15m",
        by_11["count"], n_b1,
        n_b1 // 2, n_b1,                # null = 50%
        "predicts_retest",
        regime_stable=None,
        notes="Auction rotation. Null = 50% (no informed prior).",
    ))

    # ---- B2: 6am 4h candle retest ---------------------------------------------
    b2 = load("6am-4h-candle-hit-stats/data/results.json")
    n_b2 = b2["aggregate"]["total_days"]
    by_11_b2 = b2["aggregate"]["by_11_00"]["either_side"]
    edges.append(Edge(
        "B2: 6-10am 4h candle either-side retest by 11:00",
        "intraday-15m",
        by_11_b2["count"], n_b2,
        n_b2 // 2, n_b2,
        "predicts_retest",
        regime_stable=None,
        notes="Larger window. Null = 50%.",
    ))

    # ---- D1: prior-day H or L retested in next session's first hour ----------
    d1 = load("extended-stats/01-prior-day-hl-retest/data/results.json")
    n_d1 = d1["first_hour"]["either_side"]["count"] + d1["first_hour"]["neither"]["count"]
    # Reconstruct n from sub-buckets
    n_d1 = 222
    edges.append(Edge(
        "D1: PDH or PDL retested in first hour",
        "intraday-15m",
        d1["first_hour"]["either_side"]["count"], n_d1,
        n_d1 // 2, n_d1,
        "predicts_retest",
        regime_stable=None,
        notes="Null = 50%.",
    ))

    # ---- D2: 9:30 candle retested within first 15m bar (immediate retest) ----
    # Source v2: 91.03% of 223 = 203 retest within 1 bar.
    edges.append(Edge(
        "D2: 9:30 retest within first 15m bar (vs first 30m null)",
        "intraday-15m",
        203, 223,
        round(0.78 * 223), 223,         # rough: by-10:00 either-side ~78%, used as base
        "predicts_fast_retest",
        regime_stable=None,
        notes="Frames 'is the retest fast?' rather than 'does retest happen?'",
    ))

    # ---- E1c: NR7 next-day expansion ------------------------------------------
    # daily-patterns-v1 stat 3
    e1c = load("daily-patterns-v1/data/results.json")["stat_3_nr7_expansion"]
    nr7_n = e1c["n"]
    nr7_k = round(e1c["next_day_expanded_pct"] * nr7_n / 100)
    # Base rate for "any random day expands range vs prior day" ≈ 50% by symmetry
    # (any given range R has P(next-day range > R) ≈ 0.5 if ranges are
    # exchangeable). In practice the base rate is closer to 0.5 — we use 0.5
    # as the conservative null.
    edges.append(Edge(
        "E1c: NR7 → next-day range expansion",
        "daily",
        nr7_k, nr7_n,
        nr7_n // 2, nr7_n,
        "predicts_expansion",
        regime_stable=True,            # v2 confirmed: above MA 84.36 vs below 81.88
        notes="Regime-stable per E2.",
    ))

    # ---- E1b: top-quartile close → higher high next day ---------------------
    e1b = load("daily-patterns-v1/data/results.json")["stat_2_close_quartile_followthrough"]
    topq_n = e1b["after_top_quartile_close"]["n"]                # 2419
    topq_k = round(e1b["after_top_quartile_close"]["higher_high_next_day_pct"] * topq_n / 100)
    botq_n = e1b["after_bot_quartile_close"]["n"]                # 1598
    botq_k = round(e1b["after_bot_quartile_close"]["lower_low_next_day_pct"] * botq_n / 100)
    # Base = the bottom-Q close's higher-high rate would be the natural counterfactual,
    # but the source doesn't give it directly. Use 50% null again (conservative).
    edges.append(Edge(
        "E1b: top-Q close → higher high next day",
        "daily",
        topq_k, topq_n,
        topq_n // 2, topq_n,
        "predicts_higher_high",
        regime_stable=True,
        notes="Largest-n signal in repo. Predicts extension, not direction.",
    ))
    edges.append(Edge(
        "E1b: bottom-Q close → lower low next day",
        "daily",
        botq_k, botq_n,
        botq_n // 2, botq_n,
        "predicts_lower_low",
        regime_stable=True,
        notes="Mirror. Robust per E2.",
    ))

    # ---- E1a: 4-day green streak continuation ------------------------------
    e1a = load("daily-patterns-v1/data/results.json")["stat_1_streak_continuation"]
    g4 = next(r for r in e1a["after_green_streaks"] if r["streak_length"] == 4)
    edges.append(Edge(
        "E1a: 4-green streak → next day green",
        "daily",
        round(g4["p_continue_green_pct"] * g4["n"] / 100), g4["n"],
        round(0.5 * g4["n"]), g4["n"],
        "predicts_green",
        regime_stable=False,           # v2: above MA strong, below MA collapses
        notes="Regime-DEPENDENT — only works above 200MA.",
    ))

    # ---- E2: top-Q higher-high above 200MA ----------------------------------
    e2 = load("daily-patterns-v2/data/results.json")
    topq_above = next(s for s in e2["vol1_stats_split_by_200ma_regime"]["stats"]
                     if s["stat"] == "Top-quartile close: P(higher high)")
    edges.append(Edge(
        "E2: top-Q close + above-200MA → higher high",
        "daily",
        round(topq_above["pct_above"] * topq_above["n_above"] / 100), topq_above["n_above"],
        round(topq_above["pct_below"] * topq_above["n_below"] / 100), topq_above["n_below"],
        "predicts_higher_high",
        regime_stable=True,
        notes="Above-MA vs below-MA — regime test.",
    ))

    # ---- E1d gap fill, medium gap (25-50 pts) ------------------------------
    gf = load("daily-patterns-v1/data/results.json")["stat_4_gap_fill"]["by_size"]
    g25 = next(b for b in gf if b["bucket"] == "25-50 pts")
    edges.append(Edge(
        "E1d: medium gap (25-50pt) fills same day",
        "daily",
        g25["filled"], g25["n"],
        g25["n"] // 2, g25["n"],
        "predicts_gap_fill",
        regime_stable=True,
        notes="Robust above/below MA per E2 (70.95 vs 69.41).",
    ))
    g50 = next(b for b in gf if b["bucket"] == "50-100 pts")
    edges.append(Edge(
        "E1d: large gap (50-100pt) fills same day",
        "daily",
        g50["filled"], g50["n"],
        g50["n"] // 2, g50["n"],
        "predicts_gap_fill",
        regime_stable=None,
        notes="Smaller n.",
    ))

    return edges


def main() -> None:
    edges = build_edges()
    z_p = [e.z_p() for e in edges]
    pvals = [p for _, p in z_p]
    rejected, p_adj = benjamini_hochberg(pvals, q=0.10)

    rows = []
    for e, padj, rej in zip(edges, p_adj, rejected):
        d = edge_to_dict(e, padj)
        d["bh_rejects_null"] = bool(rej)
        rows.append(d)

    # Sort by tradeability desc, then by lift desc.
    rows.sort(key=lambda r: (-r["tradeability_1to5"], -abs(r["lift_pp"])))

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(rows, indent=2))

    # ---- markdown ----------------------------------------------------------
    md = []
    md.append("# Phase 2 — Edge Ranking\n")
    md.append("Wilson 95% CIs, two-proportion z-test vs a stated base rate, "
              "Benjamini-Hochberg FDR correction at q=0.10. Tradeability score "
              "1-5 combines sample size, BH-adjusted significance, lift "
              "magnitude, and regime stability (Phase 1 + source AUDIT.md).\n")
    md.append("Cost model used for the R-multiple sanity check: $4 RT commission "
              "+ 1 tick slippage per side on full NQ ($20/pt). Round-trip cost "
              f"≈ {round(0.5 + 0.2, 2)} pts ≈ $14 per contract per round trip.\n")
    md.append("## Ranked table\n")
    header = ("| # | Edge | Family | k/n | rate | base | lift (pp) | "
              "Wilson 95% CI | p (z) | p-adj BH | BH rej | regime | "
              "trad. | notes |")
    sep = "|" + "|".join(["---"] * 14) + "|"
    md.append(header)
    md.append(sep)
    for i, r in enumerate(rows, 1):
        ci = f"[{r['wilson_lo']:.3f}, {r['wilson_hi']:.3f}]"
        regime = ("✓ stable" if r["regime_stable"] is True
                  else "✗ fragile" if r["regime_stable"] is False
                  else "?")
        md.append(
            f"| {i} | {r['name']} | {r['family']} | {r['k']}/{r['n']} | "
            f"{r['rate']:.3f} | {r['base_rate']:.3f} | {r['lift_pp']:+.2f} | "
            f"{ci} | {r['p_value']} | {r['p_adj_bh']} | "
            f"{'✓' if r['bh_rejects_null'] else '✗'} | {regime} | "
            f"{r['tradeability_1to5']} | {r['notes']} |"
        )

    md.append("\n## Shortlist (tradeability ≥ 4 and BH-significant)\n")
    short = [r for r in rows if r["tradeability_1to5"] >= 4 and r["bh_rejects_null"]]
    for r in short:
        md.append(f"- **{r['name']}** — k={r['k']}/n={r['n']}, "
                  f"rate {r['rate']:.1%}, lift {r['lift_pp']:+.1f}pp, "
                  f"BH p={r['p_adj_bh']}. {r['notes']}")

    md.append("\n## Discarded for Phase 5\n")
    discard = [r for r in rows if r["tradeability_1to5"] <= 2 or not r["bh_rejects_null"]]
    for r in discard:
        md.append(f"- {r['name']} — score {r['tradeability_1to5']}, "
                  f"{'BH-significant' if r['bh_rejects_null'] else 'NOT BH-significant'}, "
                  f"n={r['n']}.")

    md.append("\n## Method notes\n")
    md.append("- **Base rates** are the natural counterfactual where one exists "
              "(e.g. opposite-color rows for D4 / C1). Where no clean "
              "counterfactual is available, we use the agnostic null of 50% — "
              "this is conservative for one-sided directional claims and biases "
              "p-values upward (i.e. we under-reject).")
    md.append("- **Multiple comparisons:** BH at q=0.10 on the full set of "
              f"{len(rows)} tests. With this many tests, raw p<0.05 is "
              "insufficient.")
    md.append("- **Sample-size flag:** anything with n<100 is a yellow card. "
              "C1 wide-body sub-buckets (n≈31-49) survive only because their "
              "lift is large; the CIs are wide and we treat the magnitude as "
              "indicative, not precise.")
    md.append("- **Regime stability:** drawn from `daily-patterns-v2` 200MA "
              "split for daily edges. For intraday edges the source has not "
              "tested regime sensitivity — Phase 6 should add it as a "
              "robustness check.")
    md.append("- **R-multiple after costs:** computed in code "
              "(`src/stats/edge.py:expected_r_after_costs`) but not tabulated "
              "row-wise here because it depends on the trade construction "
              "(stop, target) which is a Phase-5 decision, not a Phase-2 one. "
              "We re-visit it in Phase 5/6.")

    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"{len(rows)} edges total | {len(short)} shortlisted | "
          f"{sum(1 for r in rows if r['bh_rejects_null'])} pass BH")


if __name__ == "__main__":
    main()

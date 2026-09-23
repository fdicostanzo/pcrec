"""[nocapsview] the nocaps-vs-nocaps ledger (D119 addendum, Frank 2026-09-23:
"we should compare capturing vs capturing and non-capturing vs non-capturing
... a cell never crosses classes"), REVISED after pcrec-bench's authoritative
run-derived classification table (I-99 ack, e8c5a12; I-100 rulings,
5435ac6/e8d6109) and Frank's standing cross-class anomaly query (I-101,
7f440dd).

Reads FOUR sources, all read-only:
  1. docs/dev/optloop/cycle1_rows.tsv -- the 125-row ranked-cell population
     (pattern, regime, family, weight), unchanged from cycle 1's own
     class-weighting.
  2. pcrec-bench/reports/2026-09-20-capability-0.1-budu-ryzen1600-fullroster-25b1984f.tsv
     -- the BEFORE report, full roster.
  3. pcrec-bench/reports/2026-09-23-capability-0.1-budu-ryzen1600-after-8d716693.tsv
     -- the AFTER report (pcrec's two pins + oniguruma/rust/vectorscan spot
     checks only -- NO pcre2-dfa, pcre2-interp/jit, re2, or tre row at all).
  3. pcrec-bench/docs/dev/inbox_from_pcrec.md (commits e8c5a12, 5435ac6,
     e8d6109) -- the FROZEN classification table this script codifies as
     NOCAPS_TESTEES / YES_TESTEES below. NOT re-derived from configs.toml
     here -- see cycle1_nocaps_view.md Sec.1 for the citation and the
     disagreement this ruling has with a naive configs.toml/testee_id read
     (rust-default's testee_id still says "-caps-"; the table, not the id,
     is the views' authority per I-100 point 3).

Nothing recompiled, nothing re-measured.
"""
import csv, json, math, collections

BENCH = "/Users/fdicostanzo/pcrec-bench"
BEFORE_TSV = BENCH + "/reports/2026-09-20-capability-0.1-budu-ryzen1600-fullroster-25b1984f.tsv"
AFTER_TSV = BENCH + "/reports/2026-09-23-capability-0.1-budu-ryzen1600-after-8d716693.tsv"
ROWS_TSV = "/Users/fdicostanzo/pcrec/worktrees/nocapsview/docs/dev/optloop/cycle1_rows.tsv"
OUT_DIR = "/Users/fdicostanzo/pcrec/worktrees/nocapsview/docs/dev/optloop/nocapsview/"

REGIME_MAP = {
    "large-subject-throughput": "thr",
    "short-subject-search": "srch",
}

NULL_BAND_LO = -5.7393   # O-48 Block B, two-sided, 120 cells
NULL_BAND_HI = 8.4605

PC_NOCAPS_BEFORE = "pcrec_25b1984f_auto-nocaps-simdna"
PC_NOCAPS_AFTER = "pcrec_8d716693_auto-nocaps-simdna"
PC_CAPS_BEFORE = "pcrec_25b1984f_auto-caps-simdna"
PC_CAPS_AFTER = "pcrec_8d716693_auto-caps-simdna"

# ---- the FROZEN classification (pcrec-bench e8c5a12 / 5435ac6 / e8d6109) ----
DFA = "libpcre2_10.46_dfa-nocaps-simdna"
RUST = "rust_1.13.1_default-caps-simdna"          # id says caps; table says NO (I-100)
VECTORSCAN = "vectorscan_5.4.11_block-nosom-nocaps-simd"   # NO, SIMD-excluded from algorithmic target

# NOCAPS class competitor set for the SCORED ranking: pcre2-dfa is
# algorithmic; rust-default is ruled NO (I-100 #2) but carries the declared
# captures_at caveat (Sec.1); vectorscan is NO but SIMD-excluded (unchanged
# from cycle 1 Sec.0 rule 2) -- never a scoring target.
NOCAPS_SCORED = [DFA, RUST]

# YES class for Sec.6's anomaly query (I-101): every config the frozen
# table declares captures-assigning on EVERY run.
YES_TESTEES = [
    "libpcre2_10.46_interp-caps-simdna",
    "libpcre2_10.46_jit-caps-simdna",
    "re2_11.0.0_default-caps-simdna",
    "re2_11.0.0_longest-caps-simdna",
    "oniguruma_6.9.10_default-caps-simdna",
    "tre_0.9.0_default-caps-simdna",
]

ALL_WANTED = set(NOCAPS_SCORED + YES_TESTEES + [
    PC_NOCAPS_BEFORE, PC_NOCAPS_AFTER, PC_CAPS_BEFORE, PC_CAPS_AFTER,
])


def load_rows():
    pop = []
    with open(ROWS_TSV) as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            pop.append({
                "pattern": row["pattern"],
                "regime": REGIME_MAP.get(row["regime"], row["regime"]),
                "family": row["family"],
                "weight": float(row["weight"]),
            })
    return pop


def load_report(path, wanted_testees):
    """-> dict[(pattern, regime)][testee] = {"status", "ns", "min_ns", "max_ns"}"""
    out = collections.defaultdict(dict)
    with open(path) as f:
        for line in f:
            if not line.startswith("rank\t"):
                continue
            parts = line.rstrip("\n").split("\t")
            pattern = parts[1]
            regime_or_na = parts[3]
            testee = parts[6]
            status = parts[7]
            metric = parts[10] if len(parts) > 10 else ""
            value = parts[11] if len(parts) > 11 else ""
            if testee not in wanted_testees:
                continue
            regime = REGIME_MAP.get(regime_or_na)
            if regime is None:
                continue
            key = (pattern, regime)
            entry = out[key].setdefault(testee, {"status": status, "ns": None, "min_ns": None, "max_ns": None})
            entry["status"] = status
            if value:
                try:
                    fv = float(value)
                except ValueError:
                    continue
                if metric == "median_ns":
                    entry["ns"] = fv
                elif metric == "min_ns":
                    entry["min_ns"] = fv
                elif metric == "max_ns":
                    entry["max_ns"] = fv
    return out


def score_of(weight, ratio):
    if ratio is None or ratio <= 1.0:
        return 0.0
    return weight * math.log2(ratio)


def ok(e):
    return e is not None and e.get("status") == "measured" and e.get("ns") is not None


def best_of(cells_map, testees):
    """-> (best_testee_id, best_ns) among `testees`, or (None, None)."""
    best_t, best_ns = None, None
    for t in testees:
        e = cells_map.get(t)
        if ok(e) and (best_ns is None or e["ns"] < best_ns):
            best_t, best_ns = t, e["ns"]
    return best_t, best_ns


def main():
    pop = load_rows()
    before = load_report(BEFORE_TSV, ALL_WANTED)
    after = load_report(AFTER_TSV, ALL_WANTED)

    out_rows = []
    for r in pop:
        key = (r["pattern"], r["regime"])
        b = before.get(key, {})
        a = after.get(key, {})

        row = dict(r)

        # --- pcrec's own nocaps/caps numbers, both pins ---
        row["before_nocaps_ns"] = b[PC_NOCAPS_BEFORE]["ns"] if ok(b.get(PC_NOCAPS_BEFORE)) else None
        row["after_nocaps_ns"] = a[PC_NOCAPS_AFTER]["ns"] if ok(a.get(PC_NOCAPS_AFTER)) else None
        row["paired_before_nocaps_ns"] = a[PC_NOCAPS_BEFORE]["ns"] if ok(a.get(PC_NOCAPS_BEFORE)) else None
        row["before_caps_ns"] = b[PC_CAPS_BEFORE]["ns"] if ok(b.get(PC_CAPS_BEFORE)) else None
        row["after_caps_ns"] = a[PC_CAPS_AFTER]["ns"] if ok(a.get(PC_CAPS_AFTER)) else None

        # --- NOCAPS-scored competitor: best of {pcre2-dfa, rust-default} ---
        # BEFORE: both from the fullroster (before) report.
        bt_before, bns_before = best_of(b, NOCAPS_SCORED)
        row["before_nocaps_competitor"] = bt_before
        row["before_nocaps_competitor_ns"] = bns_before
        # AFTER: rust is RE-MEASURED in the after report; pcre2-dfa is not
        # (absent from that roster) -- reused from the BEFORE report, the
        # one assumption this view still carries (Sec.0).
        after_dfa = b.get(DFA)  # reused, not from `a`
        after_rust = a.get(RUST)  # re-measured
        cand = {}
        if ok(after_dfa):
            cand[DFA] = after_dfa["ns"]
        if ok(after_rust):
            cand[RUST] = after_rust["ns"]
        if cand:
            bt_after = min(cand, key=cand.get)
            row["after_nocaps_competitor"] = bt_after
            row["after_nocaps_competitor_ns"] = cand[bt_after]
        else:
            row["after_nocaps_competitor"] = None
            row["after_nocaps_competitor_ns"] = None

        row["before_ratio"] = (row["before_nocaps_ns"] / row["before_nocaps_competitor_ns"]
                                if row["before_nocaps_ns"] and row["before_nocaps_competitor_ns"] else None)
        row["before_score"] = score_of(row["weight"], row["before_ratio"])
        row["after_ratio"] = (row["after_nocaps_ns"] / row["after_nocaps_competitor_ns"]
                               if row["after_nocaps_ns"] and row["after_nocaps_competitor_ns"] else None)
        row["after_score"] = score_of(row["weight"], row["after_ratio"])

        if row["paired_before_nocaps_ns"] and row["after_nocaps_ns"] is not None:
            row["delta_pct"] = (row["after_nocaps_ns"] - row["paired_before_nocaps_ns"]) / row["paired_before_nocaps_ns"] * 100.0
        else:
            row["delta_pct"] = None

        # --- Sec.6: cross-class anomaly query ---
        # YES-class best, BEFORE (all six available in the fullroster report).
        yt_before, yns_before = best_of(b, YES_TESTEES)
        row["before_yes_best_testee"] = yt_before
        row["before_yes_best_ns"] = yns_before
        row["before_nocaps_min_ns"] = b[PC_NOCAPS_BEFORE]["min_ns"] if b.get(PC_NOCAPS_BEFORE) else None
        row["before_nocaps_max_ns"] = b[PC_NOCAPS_BEFORE]["max_ns"] if b.get(PC_NOCAPS_BEFORE) else None
        if yt_before:
            row["before_yes_competitor_max_ns"] = b[yt_before]["max_ns"]
        else:
            row["before_yes_competitor_max_ns"] = None

        # YES-class best, AFTER: only oniguruma is re-measured in the after
        # report; the rest (pcre2-interp/jit, re2 x2, tre) are reused from
        # the BEFORE report -- flagged explicitly in Sec.6's methodology.
        onig_after = a.get("oniguruma_6.9.10_default-caps-simdna")
        reused_yes = {t: b[t]["ns"] for t in YES_TESTEES if t != "oniguruma_6.9.10_default-caps-simdna" and ok(b.get(t))}
        cand2 = dict(reused_yes)
        if ok(onig_after):
            cand2["oniguruma_6.9.10_default-caps-simdna"] = onig_after["ns"]
        if cand2:
            yt_after = min(cand2, key=cand2.get)
            row["after_yes_best_testee"] = yt_after
            row["after_yes_best_ns"] = cand2[yt_after]
        else:
            row["after_yes_best_testee"] = None
            row["after_yes_best_ns"] = None
        row["after_nocaps_min_ns"] = a[PC_NOCAPS_AFTER]["min_ns"] if a.get(PC_NOCAPS_AFTER) else None
        row["after_nocaps_max_ns"] = a[PC_NOCAPS_AFTER]["max_ns"] if a.get(PC_NOCAPS_AFTER) else None
        if row["after_yes_best_testee"] == "oniguruma_6.9.10_default-caps-simdna" and ok(onig_after):
            row["after_yes_competitor_max_ns"] = onig_after["max_ns"]
        elif row["after_yes_best_testee"]:
            row["after_yes_competitor_max_ns"] = b[row["after_yes_best_testee"]]["max_ns"]
        else:
            row["after_yes_competitor_max_ns"] = None

        # rust as a SECONDARY, informational YES-check (Frank's literal
        # text named it; I-100 rules it NO for the scored views -- kept
        # separate and clearly labeled, never merged into the table above).
        row["before_rust_ns"] = b[RUST]["ns"] if ok(b.get(RUST)) else None
        row["after_rust_ns"] = a[RUST]["ns"] if ok(a.get(RUST)) else None

        # mirror: does pcrec's CAPTURING default beat every non-capturing
        # competitor (dfa, rust, vectorscan excluded)?
        row["before_caps_vs_nocaps_competitor"] = (
            row["before_caps_ns"] < row["before_nocaps_competitor_ns"]
            if row["before_caps_ns"] and row["before_nocaps_competitor_ns"] else None
        )
        row["after_caps_vs_nocaps_competitor"] = (
            row["after_caps_ns"] < row["after_nocaps_competitor_ns"]
            if row["after_caps_ns"] and row["after_nocaps_competitor_ns"] else None
        )

        out_rows.append(row)

    json.dump(out_rows, open(OUT_DIR + "nocaps_rows.json", "w"), indent=1)

    def classify(ratio):
        if ratio is None:
            return "no-data"
        return "win-or-tie" if ratio <= 1.0 else "loss"

    for tag, rk, sk in (("BEFORE", "before_ratio", "before_score"), ("AFTER", "after_ratio", "after_score")):
        wins = losses = nodata = 0
        total_loss_score = 0.0
        for row in out_rows:
            c = classify(row[rk])
            if c == "win-or-tie":
                wins += 1
            elif c == "loss":
                losses += 1
                total_loss_score += row[sk]
            else:
                nodata += 1
        print(f"{tag}: scorable={wins+losses} win/tie={wins} loss={losses} no-data={nodata} loss_score_total={total_loss_score:.4f}")

    # Sec.6 anomaly counts
    for tag, ynk, nnk in (("BEFORE", "before_yes_best_ns", "before_nocaps_ns"), ("AFTER", "after_yes_best_ns", "after_nocaps_ns")):
        n = sum(1 for row in out_rows if row[ynk] is not None and row[nnk] is not None and row[ynk] < row[nnk])
        print(f"{tag} anomaly cells (YES-class faster than our nocaps): {n}")

    with open(OUT_DIR + "nocaps_rows.tsv", "w", newline="") as f:
        cols = list(out_rows[0].keys())
        w = csv.writer(f, delimiter="\t")
        w.writerow(cols)
        for row in out_rows:
            w.writerow([row[c] for c in cols])


if __name__ == "__main__":
    main()

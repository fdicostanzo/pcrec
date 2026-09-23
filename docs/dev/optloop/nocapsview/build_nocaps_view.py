"""[nocapsview] the nocaps-vs-nocaps ledger (D119 addendum, Frank 2026-09-23:
"we should compare capturing vs capturing and non-capturing vs non-capturing
... a cell never crosses classes").

Reads THREE sources, all read-only:
  1. docs/dev/optloop/cycle1_rows.tsv -- the 125-row ranked-cell population
     (pattern, regime, family, weight), unchanged from cycle 1's own
     class-weighting (cycle1_analysis.md Sec.0).
  2. pcrec-bench/reports/2026-09-20-capability-0.1-budu-ryzen1600-fullroster-25b1984f.tsv
     -- the BEFORE report, full roster (has libpcre2_10.46_dfa-nocaps-simdna).
  3. pcrec-bench/reports/2026-09-23-capability-0.1-budu-ryzen1600-after-8d716693.tsv
     -- the AFTER report, narrowed roster (oniguruma/rust/vectorscan spot
     checks + pcrec's four configs at BOTH pins 25b1984f and 8d716693) --
     NO pcre2-dfa row at all.

Nothing recompiled, nothing re-measured; this script only re-reads committed
report files and cycle 1's own committed ranked-cell table.

Captures classification (Step 1) is NOT computed here -- it is a one-time
read of testees/*/configs.toml, recorded by hand in cycle1_nocaps_view.md
Sec.1. This script only consumes the two facts that follow from it: pcrec's
nocaps testee is `auto-nocaps` (`captures = "off"` in
testees/pcrec/configs.toml), and the one algorithmic nocaps competitor is
`libpcre2_10.46_dfa-nocaps-simdna` (`captures = "off"` in
testees/pcre2/configs.toml, cross-confirmed by
pcrec-bench/tools/selfcheck.py:9858's own assertion
"pcre2-dfa declares captures=off"). vectorscan is excluded per cycle 1
Sec.0 rule 2 (SIMD, boolean grain, no scalar mechanism).
"""
import csv, json, math, collections

BENCH = "/Users/fdicostanzo/pcrec-bench"
BEFORE_TSV = BENCH + "/reports/2026-09-20-capability-0.1-budu-ryzen1600-fullroster-25b1984f.tsv"
AFTER_TSV = BENCH + "/reports/2026-09-23-capability-0.1-budu-ryzen1600-after-8d716693.tsv"
ROWS_TSV = "/Users/fdicostanzo/pcrec/worktrees/nocapsview/docs/dev/optloop/cycle1_rows.tsv"

REGIME_MAP = {
    "large-subject-throughput": "thr",
    "short-subject-search": "srch",
}

NULL_BAND_LO = -5.7393   # O-48 Block B, two-sided, 120 cells
NULL_BAND_HI = 8.4605


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
    """-> dict[(pattern, regime)][testee] = {"status":..., "ns": float|None}"""
    out = collections.defaultdict(dict)
    with open(path) as f:
        for line in f:
            if not line.startswith("rank\t"):
                continue
            parts = line.rstrip("\n").split("\t")
            # section pattern subject_or_na regime_or_na form fact testee status tier rank metric value n ...
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
            entry = out[key].setdefault(testee, {"status": status, "ns": None})
            entry["status"] = status
            if metric == "median_ns" and value:
                try:
                    entry["ns"] = float(value)
                except ValueError:
                    pass
    return out


def score_of(weight, ratio):
    if ratio is None or ratio <= 1.0:
        return 0.0
    return weight * math.log2(ratio)


def main():
    pop = load_rows()

    before_wanted = {"pcrec_25b1984f_auto-nocaps-simdna", "libpcre2_10.46_dfa-nocaps-simdna"}
    after_wanted = {"pcrec_25b1984f_auto-nocaps-simdna", "pcrec_8d716693_auto-nocaps-simdna"}

    before = load_report(BEFORE_TSV, before_wanted)
    after = load_report(AFTER_TSV, after_wanted)

    PC_NOCAPS_BEFORE = "pcrec_25b1984f_auto-nocaps-simdna"
    PC_NOCAPS_AFTER = "pcrec_8d716693_auto-nocaps-simdna"
    DFA = "libpcre2_10.46_dfa-nocaps-simdna"

    out_rows = []
    for r in pop:
        key = (r["pattern"], r["regime"])
        b = before.get(key, {})
        a = after.get(key, {})

        b_nocaps = b.get(PC_NOCAPS_BEFORE)
        b_dfa = b.get(DFA)
        a_nocaps_before_pin = a.get(PC_NOCAPS_BEFORE)  # same pin, in the AFTER report's own window
        a_nocaps_after_pin = a.get(PC_NOCAPS_AFTER)

        def ok(e):
            return e is not None and e.get("status") == "measured" and e.get("ns") is not None

        row = dict(r)
        row["before_nocaps_ns"] = b_nocaps["ns"] if ok(b_nocaps) else None
        row["before_nocaps_status"] = b_nocaps["status"] if b_nocaps else "absent"
        row["dfa_ns"] = b_dfa["ns"] if ok(b_dfa) else None
        row["dfa_status"] = b_dfa["status"] if b_dfa else "absent"
        row["after_nocaps_ns"] = a_nocaps_after_pin["ns"] if ok(a_nocaps_after_pin) else None
        row["after_nocaps_status"] = a_nocaps_after_pin["status"] if a_nocaps_after_pin else "absent"
        row["paired_before_nocaps_ns"] = a_nocaps_before_pin["ns"] if ok(a_nocaps_before_pin) else None

        # BEFORE ranking: pcrec auto-nocaps (fullroster pin) vs pcre2-dfa (fullroster pin)
        if row["before_nocaps_ns"] is not None and row["dfa_ns"] is not None:
            row["before_ratio"] = row["before_nocaps_ns"] / row["dfa_ns"]
        else:
            row["before_ratio"] = None
        row["before_score"] = score_of(row["weight"], row["before_ratio"])

        # AFTER ranking: pcrec auto-nocaps (after-report pin 8d716693) vs pcre2-dfa
        # (fullroster pin 25b1984f -- pcre2-dfa is not re-measured in the after
        # report at all; see Sec.0's methodology note).
        if row["after_nocaps_ns"] is not None and row["dfa_ns"] is not None:
            row["after_ratio"] = row["after_nocaps_ns"] / row["dfa_ns"]
        else:
            row["after_ratio"] = None
        row["after_score"] = score_of(row["weight"], row["after_ratio"])

        # Batch-1 own Delta%: paired same-window pcrec-only comparison
        # (both pins read from the SAME after-report window, the ledger's
        # own apples-to-apples pairing) -- independent of the competitor.
        if row["paired_before_nocaps_ns"] and row["after_nocaps_ns"] is not None:
            row["delta_pct"] = (row["after_nocaps_ns"] - row["paired_before_nocaps_ns"]) / row["paired_before_nocaps_ns"] * 100.0
        else:
            row["delta_pct"] = None

        out_rows.append(row)

    json.dump(out_rows, open("/Users/fdicostanzo/pcrec/worktrees/nocapsview/docs/dev/optloop/nocapsview/nocaps_rows.json", "w"), indent=1)

    # ---- summary classification ----
    def classify(ratio):
        if ratio is None:
            return "no-data"
        if ratio <= 1.0:
            return "win-or-tie"
        return "loss"

    for tag, ratio_key, score_key in (("BEFORE", "before_ratio", "before_score"),
                                       ("AFTER", "after_ratio", "after_score")):
        wins = losses = nodata = 0
        total_loss_score = 0.0
        for row in out_rows:
            c = classify(row[ratio_key])
            if c == "win-or-tie":
                wins += 1
            elif c == "loss":
                losses += 1
                total_loss_score += row[score_key]
            else:
                nodata += 1
        print(f"{tag}: scorable={wins+losses} win/tie={wins} loss={losses} no-data={nodata} loss_score_total={total_loss_score:.4f}")

    with open("/Users/fdicostanzo/pcrec/worktrees/nocapsview/docs/dev/optloop/nocapsview/nocaps_rows.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["pattern", "regime", "family", "weight",
                    "before_nocaps_ns", "before_nocaps_status", "dfa_ns", "dfa_status",
                    "before_ratio", "before_score",
                    "after_nocaps_ns", "after_nocaps_status", "after_ratio", "after_score",
                    "paired_before_nocaps_ns", "delta_pct"])
        for row in out_rows:
            w.writerow([row["pattern"], row["regime"], row["family"], row["weight"],
                        row["before_nocaps_ns"], row["before_nocaps_status"], row["dfa_ns"], row["dfa_status"],
                        row["before_ratio"], row["before_score"],
                        row["after_nocaps_ns"], row["after_nocaps_status"], row["after_ratio"], row["after_score"],
                        row["paired_before_nocaps_ns"], row["delta_pct"]])


if __name__ == "__main__":
    main()

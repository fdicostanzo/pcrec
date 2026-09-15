#!/usr/bin/env python3
"""docs/dev/optdial_size_sweep/join_sweep.py — [OPT-DIAL] §7 SIZE SWEEP join.

Reads the raw per-pass SIZELOG tables run_sweep.sh produces
(docs/dev/optdial_size_sweep/runs/<slug>_size.tsv, the same format
tests/size/run_size_log.sh assembles into docs/dev/artifact_size_log.tsv:
`<file>:<line>\tengine\trungs\tprefilter\tsize_bytes\tgcc_cpu_s\tgcc_wall_s\tload1`,
no header row on the per-pass raw files) and, for each flag pass, joins it
against the baseline pass BY KEY (`file:line`, the .rxt block's own
coordinates — stable across an emitter change, the same key
tests/axes/dump_diff.awk uses to compare answers).

Prints, per flag: the matched population (keys present in BOTH baseline
and the flag pass), the LOST/GAINED counts (a key present on one side
only — LOST is baseline-only, i.e. the pattern stopped compiling under
the flag; GAINED is flag-only, which none of these seven deny-only flags
is documented to ever produce), the mover count and fraction (delta != 0
bytes), and the FULL distribution over movers (not just the median) —
min, p10, p50 (median), p90, p99, max, plus the single biggest grower and
shrinker by name. A flag whose mover count is 0 is printed as a FINDING
in the same table, never silently averaged into a "no effect" line that
looks like every other zero.

Also cross-checks each flag's *_dump.tsv (RXTDUMP, if present) for
REFUSED rows — K35: any refusal population is counted and named, not
assumed away, even though tuning.md documents all seven of these flags as
deny-only (never refusing under default engine selection).

Usage:
    python3 docs/dev/optdial_size_sweep/join_sweep.py [--tsv-out FILE]

Writes a human-readable report to stdout; --tsv-out additionally writes a
machine-readable per-flag summary table (one row per flag) for the memo
to quote directly rather than transcribe by hand.
"""
import sys
import os
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")

PASSES = [
    ("possessify",     "-fno-possessify",     "PCREC_NO_POSSESSIFY",   4,  "2.1"),
    ("revdet",         "-fno-revdet",         "PCREC_NO_REVDET",       5,  "2.2"),
    ("altcls_merge",   "-fno-altcls-merge",   "PCREC_NO_ALTCLS_MERGE", 10, "2.6"),
    ("altcls_factor",  "-fno-altcls-factor",  "PCREC_NO_ALTCLS_FACTOR",11, "2.7"),
    ("tiered_entry",   "-fno-tiered-entry",   "PCREC_NO_TIERED_ENTRY", 14, "2.12"),
    ("offset_skip",    "-fno-offset-skip",    "PCREC_NO_OFFSET_SKIP",  16, "2.14"),
    ("anchored_dfa",   "-fno-anchored-dfa",   "PCREC_NO_ANCHORED_DFA", 17, "2.15 (bonus, §7 item 3)"),
]


def load_size(path):
    """key -> (size_bytes, engine, rungs, prefilter)"""
    rows = {}
    if not os.path.isfile(path):
        return rows
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != 8:
                continue
            key, engine, rungs, prefilter, size_bytes, gcc_cpu, gcc_wall, load1 = parts
            try:
                sz = int(size_bytes)
            except ValueError:
                continue
            rows[key] = (sz, engine, rungs, prefilter)
    return rows


def load_dump_refused(path):
    """Count REFUSED rows in an RXTDUMP file: <file>\t<line>\t<kind>\t<route>\t<trc>\t<out>"""
    n_refused = 0
    n_total = 0
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            n_total += 1
            parts = line.split("\t")
            if len(parts) >= 5 and parts[4] == "REFUSED":
                n_refused += 1
    return (n_refused, n_total)


def percentile(sorted_vals, p):
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def analyze(base, flag_rows, label, slug):
    base_keys = set(base.keys())
    flag_keys = set(flag_rows.keys())
    matched = base_keys & flag_keys
    lost = base_keys - flag_keys        # compiled under baseline, not under the flag
    gained = flag_keys - base_keys      # compiled under the flag, not under baseline

    deltas = []  # (key, delta_bytes, base_bytes, flag_bytes)
    for k in matched:
        b_sz = base[k][0]
        f_sz = flag_rows[k][0]
        deltas.append((k, f_sz - b_sz, b_sz, f_sz))

    movers = [d for d in deltas if d[1] != 0]
    movers_sorted_by_delta = sorted(movers, key=lambda d: d[1])
    abs_sorted = sorted(m[1] for m in movers)

    report = {
        "slug": slug,
        "label": label,
        "n_base": len(base_keys),
        "n_flag": len(flag_keys),
        "n_matched": len(matched),
        "n_lost": len(lost),
        "n_gained": len(gained),
        "n_movers": len(movers),
        "pct_movers": (100.0 * len(movers) / len(matched)) if matched else 0.0,
        "lost_examples": sorted(lost)[:5],
        "gained_examples": sorted(gained)[:5],
    }
    if movers:
        report["delta_min"] = abs_sorted[0]
        report["delta_p10"] = percentile(abs_sorted, 0.10)
        report["delta_p50"] = percentile(abs_sorted, 0.50)
        report["delta_p90"] = percentile(abs_sorted, 0.90)
        report["delta_p99"] = percentile(abs_sorted, 0.99)
        report["delta_max"] = abs_sorted[-1]
        biggest_shrink = movers_sorted_by_delta[0]
        biggest_grow = movers_sorted_by_delta[-1]
        report["biggest_shrink"] = biggest_shrink
        report["biggest_grow"] = biggest_grow
        # ratio distribution too (flag_bytes / base_bytes), since a fixed
        # byte delta reads very differently on a 500-byte artifact vs a
        # 50,000-byte one
        ratios = sorted(m[3] / m[2] for m in movers if m[2] > 0)
        report["ratio_min"] = ratios[0]
        report["ratio_p50"] = percentile(ratios, 0.50)
        report["ratio_max"] = ratios[-1]
    else:
        for k in ("delta_min", "delta_p10", "delta_p50", "delta_p90",
                   "delta_p99", "delta_max", "ratio_min", "ratio_p50", "ratio_max"):
            report[k] = None
        report["biggest_shrink"] = None
        report["biggest_grow"] = None
    return report


def fmt_delta(v):
    if v is None:
        return "-"
    return f"{v:+.0f}"


def fmt_ratio(v):
    if v is None:
        return "-"
    return f"{v:.3f}x"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv-out", default=None)
    ap.add_argument("--runs-dir", default=RUNS)
    args = ap.parse_args()

    base_path = os.path.join(args.runs_dir, "baseline_size.tsv")
    base = load_size(base_path)
    if not base:
        print(f"join_sweep.py: FATAL: no baseline rows at {base_path} (has the baseline pass finished?)", file=sys.stderr)
        sys.exit(1)
    print(f"baseline: {len(base)} rows from {base_path}")
    print()

    reports = []
    for slug, cliflag, macro, bit, section in PASSES:
        sizef = os.path.join(args.runs_dir, f"{slug}_size.tsv")
        dumpf = os.path.join(args.runs_dir, f"{slug}_dump.tsv")
        flag_rows = load_size(sizef)
        if not flag_rows:
            print(f"=== {cliflag} ({macro}, bit {bit}, §{section}) — NOT YET RUN (no rows at {sizef}) ===")
            print()
            continue
        r = analyze(base, flag_rows, f"{cliflag} ({macro}, bit {bit}, §{section})", slug)
        reports.append(r)
        refused = load_dump_refused(dumpf)

        print(f"=== {r['label']} ===")
        print(f"  baseline rows={r['n_base']}  flag rows={r['n_flag']}  matched={r['n_matched']}"
              f"  lost={r['n_lost']}  gained={r['n_gained']}")
        if r["n_lost"] > 0:
            print(f"    LOST examples (compiled under baseline, not under the flag): {r['lost_examples']}")
        if r["n_gained"] > 0:
            print(f"    GAINED examples (compiled under the flag, not under baseline): {r['gained_examples']}")
        if refused is not None:
            n_ref, n_tot = refused
            print(f"  RXTDUMP: {n_ref} REFUSED of {n_tot} dumped rows"
                  + (" (K35: population counted, not assumed zero)" if n_ref else " (0 refusals — deny-only, matches tuning.md's documented posture)"))
        if r["n_movers"] == 0:
            print(f"  MOVERS: 0 of {r['n_matched']} matched patterns changed size at all.")
            print(f"  >>> FINDING: this axis moves NOTHING on the corpus population that reaches it "
                  f"(the population that cannot express this switch, per K35 — printed, never silently averaged in).")
        else:
            print(f"  MOVERS: {r['n_movers']} of {r['n_matched']} matched ({r['pct_movers']:.2f}%)")
            print(f"    byte delta over movers:  min={fmt_delta(r['delta_min'])}  p10={fmt_delta(r['delta_p10'])}"
                  f"  p50={fmt_delta(r['delta_p50'])}  p90={fmt_delta(r['delta_p90'])}"
                  f"  p99={fmt_delta(r['delta_p99'])}  max={fmt_delta(r['delta_max'])}")
            print(f"    ratio (flag/base) over movers: min={fmt_ratio(r['ratio_min'])}"
                  f"  p50={fmt_ratio(r['ratio_p50'])}  max={fmt_ratio(r['ratio_max'])}")
            k, d, b, f_ = r["biggest_shrink"]
            print(f"    biggest SHRINK: {k}  {b} -> {f_} bytes ({d:+d}, {f_/b:.3f}x)")
            k, d, b, f_ = r["biggest_grow"]
            print(f"    biggest GROW:   {k}  {b} -> {f_} bytes ({d:+d}, {f_/b:.3f}x)")
        print()

    if args.tsv_out:
        with open(args.tsv_out, "w", encoding="utf-8") as out:
            out.write("flag\tmacro\tbit\tsection\tn_matched\tn_lost\tn_gained\tn_movers\tpct_movers\t"
                       "delta_min\tdelta_p50\tdelta_p90\tdelta_p99\tdelta_max\t"
                       "ratio_min\tratio_p50\tratio_max\tbiggest_shrink_key\tbiggest_shrink_delta\t"
                       "biggest_grow_key\tbiggest_grow_delta\n")
            for r in reports:
                bs = r["biggest_shrink"]
                bg = r["biggest_grow"]
                out.write("\t".join(str(x) for x in [
                    r["label"].split(" ")[0], "", "", "",
                    r["n_matched"], r["n_lost"], r["n_gained"], r["n_movers"], f"{r['pct_movers']:.3f}",
                    r["delta_min"] if r["delta_min"] is not None else "",
                    r["delta_p50"] if r["delta_p50"] is not None else "",
                    r["delta_p90"] if r["delta_p90"] is not None else "",
                    r["delta_p99"] if r["delta_p99"] is not None else "",
                    r["delta_max"] if r["delta_max"] is not None else "",
                    f"{r['ratio_min']:.4f}" if r["ratio_min"] is not None else "",
                    f"{r['ratio_p50']:.4f}" if r["ratio_p50"] is not None else "",
                    f"{r['ratio_max']:.4f}" if r["ratio_max"] is not None else "",
                    bs[0] if bs else "", bs[1] if bs else "",
                    bg[0] if bg else "", bg[1] if bg else "",
                ]) + "\n")
        print(f"wrote {args.tsv_out}")


if __name__ == "__main__":
    main()

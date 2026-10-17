#!/usr/bin/env python3
"""memfn/data/sets/generate.py -- the kit's MEASUREMENT-SET FILES before
[MEASURE-SET] (R17-b' B1, lane fdb1; r17b_prime.md §1.6 [rev3 B6], §3.2, §5.2;
regime_eval.md Q-REVAL-10): the labelled kit-private INTERIM set and the
SYNTHETIC extreme sets, in measure_sets.md §1.2's section shape.

    python3 memfn/data/sets/generate.py [--check]

writes (or, with --check, compares byte for byte and exits 1 on a difference):
  kit-interim-grid1.tsv      grid1's values (gridread_report.md, @ 540649453),
                             relative to u = beta_walk(DFA_SCAN, r1e0c0), with
                             the derived `saving` rows computed HERE from the
                             measured absolute betas (so the derivation is
                             recomputable, measure_sets §1.6/§8.2)
  synthetic-all-walk.tsv     every saving at 0 (R0 fires, R7 never), every
                             crossover at the bound (N1 = "SIZE_MAX")
  synthetic-all-v1.tsv       every saving at 0.5 (R0 off, R7 on every shape),
                             every crossover 0 (N1 = 0)
  synthetic-all-wide.tsv     as all-v1, and the W64 block 0 (N1 = N2 = 0)
  synthetic-every-key.tsv    every key a finder row (and its pay rule) can
                             read, for every shape, form, kind and layer token
                             the shadow can spell: the R-MS1/R-MS4 tests' full
                             set and B4's "every derivable xover key" set

THE INTERIM SET IS A TEST INPUT (Q-REVAL-10): no compile reads it but through
the harness lever (`build/pcrec-harness --harness=measures=FILE`), and no
ROUTED finder row reads any set before B4. Its header says so. The interim's
`kit.eps.streamed.slope` is gridread's F3 A/A p90 (member-free single calls,
the beta slope's own regime), and it is the floor R0/R7 compare against: the
`saving` keys derive from those slopes ([rev3 C4]; finder.c's header,
fdb2_report.md). `kit.eps.findall.l64k` (F1, streamed find-all) is kept as a
measured row no B2 row reads.

values_digest: measure_sets §1.6's FNV-1a-64 over `pcrec-meas-1\\0` then, per
row in canonical (bytewise key) order, key, \\0, the unit's first byte, the
status's first byte, value_e6 as int64 LE. The byte ENCODING of unit and status
is docs/spec/measures.md's (M0); until then the first letter stands, labelled.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
U = 0.1892                              # u = beta_walk(DFA_SCAN, r1e0c0), ns/B

# gridread_report.md §2.1 (F3, MEASURED, ns/B) by cover shape (range, eq, cube):
# r1e0c0 `[0-9]`, r2e0c0 `[a-f0-9]`, r2e0c1 `[A-Za-z_]`, r3e1c0 `[0-9A-Fa-f_]`
# (r17b_prime.md §5.2 M2-M5's shapes), r0e1c1 dfa-hat's cube {f,n} + `t` (§2.1's
# 64 KiB row). The walk is flat in terms; its r0e1c1 is the 2-term walk.
SHAPES = ("r1e0c0", "r2e0c0", "r2e0c1", "r3e1c0", "r0e1c1")
BETA = {
    "WALK": (0.1892, 0.1877, 0.1896, 0.1891, 0.1877),
    "V1":   (0.1082, 0.1851, 0.2141, 0.2667, 0.1384),
    "S1":   (0.0205, 0.0334, 0.0417, 0.0540, 0.0212),
    "A1":   (0.0106, 0.0150, 0.0192, 0.0270, 0.0107),
}
R2_CLASS = ("r2e0c0", "r2e0c1", "r3e1c0")     # >= 2 RANGE terms (R0's class)


def e6(x):
    return int(round(x * 1e6))


def fnv_digest(rows):
    h = 1469598103934665603
    def feed(b):
        nonlocal h
        for c in b:
            h ^= c
            h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    feed(b"pcrec-meas-1\0")
    for r in sorted(rows, key=lambda r: r["key"].encode()):
        feed(r["key"].encode() + b"\0")
        feed(r["unit"][:1].encode())
        feed(r["status"][:1].encode())
        feed(struct.pack("<q", r["value_e6"]))
    return "%016x" % h


def row(key, unit, value, status, source, derivation="-", inputs="-", abs_ns=None):
    return {"key": key, "unit": unit, "value_e6": e6(value), "status": status,
            "derivation": derivation, "inputs": inputs, "source": source,
            "abs_ns_e6": "-" if abs_ns is None else str(e6(abs_ns))}


def interim_rows():
    rows = []
    for f, betas in BETA.items():
        for sh, b in zip(SHAPES, betas):
            src = "gridread_report.md §2.1" + (" (2-term walk: flat in terms)"
                                               if f == "WALK" and sh == "r0e1c1" else "")
            rows.append(row("kit.beta.%s.DFA_SCAN.%s" % (f, sh), "ratio", b / U, "measured",
                            src, abs_ns=b))
    # the derived savings: 1 - beta_f / beta_walk, per shape, and R0's r2 class
    sv = {}
    for f in ("V1", "S1", "A1"):
        for i, sh in enumerate(SHAPES):
            v = 1.0 - BETA[f][i] / BETA["WALK"][i]
            sv[(f, sh)] = v
            rows.append(row("kit.saving.%s.WALK.%s" % (f, sh), "ratio", v, "derived",
                            "1 - beta_f/beta_walk", "ratio-complement",
                            "kit.beta.%s.DFA_SCAN.%s;kit.beta.WALK.DFA_SCAN.%s" % (f, sh, sh)))
    best = max(R2_CLASS, key=lambda sh: sv[("V1", sh)])
    rows.append(row("kit.saving.V1.WALK.r2", "ratio", sv[("V1", best)], "derived",
                    "the r2 class: max over its measured shapes (%s)" % ",".join(R2_CLASS),
                    "max", ";".join("kit.saving.V1.WALK.%s" % s for s in R2_CLASS)))
    # the null floors per regime (gridread analysis.txt §1, A/A p90)
    rows.append(row("kit.eps.streamed.slope", "ratio", 0.00173, "measured",
                    "gridread analysis.txt F3 A/A p90 (member-free single calls)"))
    rows.append(row("kit.eps.findall.l64k", "ratio", 0.03365, "measured",
                    "gridread analysis.txt F1 A/A p90 (streamed find-all)"))
    rows.append(row("kit.eps.ext.engine", "ratio", 0.00382, "measured",
                    "gridread analysis.txt EXT A/A p90"))
    # the per-call fixed part F (§2.2, MEASURED), in walk bytes
    for n, vals in ((64, (4.74, 4.18, 4.70, 4.98)), (48, (4.84, 4.17, 24.54, 14.73))):
        for f, ns in zip(("WALK", "V1", "S1", "A1"), vals):
            rows.append(row("kit.f.%s.DFA_SCAN.n%d" % (f, n), "walkbytes", ns / U, "measured",
                            "gridread_report.md §2.2", abs_ns=ns))
    # the single-call crossovers (§4.3, INTERPOLATED) and the block (DERIVED)
    for f, b, note in (("V1", 36, "INTERPOLATED(32,48)"), ("S1", 18, "INTERPOLATED(8,32)"),
                       ("A1", 20, "INTERPOLATED(8,32)")):
        rows.append(row("kit.xover.%s.WALK.DFA_SCAN" % f, "bytes", b, "derived",
                        "gridread_report.md §4.3, %s" % note, "interp-log2"))
    rows.append(row("kit.block.W64", "bytes", 64, "derived", "W = 64 (§4.4: the step at n 63->64)",
                    "step"))
    # the single-call delta V1 - walk (§4.3/§4.4, M12), walk bytes
    for n, ns in ((8, 2.3), (32, 0.6), (48, -4.5), (63, -5.6)):
        rows.append(row("kit.delta.V1.WALK.DFA_SCAN.n%d" % n, "walkbytes", ns / U, "measured",
                        "gridread_report.md §4.3-§4.4", abs_ns=ns))
    # c_cold (§2.4, M13) and the warm use (§2.3, M14), walk bytes
    for f, ns in (("V1", 2.47), ("S1", 2.90), ("A1", 2.91)):
        rows.append(row("kit.ccold.%s.DFA_SCAN" % f, "walkbytes", ns / U, "measured",
                        "gridread_report.md §2.4 (relative to the walk)", abs_ns=ns))
    for f, ns in (("WALK", 1.67), ("V1", 2.38), ("S1", 2.22), ("A1", 2.23)):
        rows.append(row("kit.wuse.%s.DFA_SCAN" % f, "walkbytes", ns / U, "measured",
                        "gridread_report.md §2.3", abs_ns=ns))
    # g* (§4.1, interpolated; the LOWER end of each measured range)
    for f, k, g in (("V1", "DFA_SCAN", 10.8), ("V1", "DFA_HAT", 3.0), ("S1", "DFA_SCAN", 4.3),
                    ("S1", "DFA_HAT", 2.1), ("A1", "DFA_SCAN", 4.2), ("A1", "DFA_HAT", 2.1)):
        rows.append(row("kit.gstar.%s.%s" % (f, k), "bytes", g, "derived",
                        "gridread_report.md §4.1 (the range's lower end)", "interp-log2"))
    return rows


ALL_SHAPES = tuple("r%de%dc%d" % (r, e, c) for r in range(5) for e in range(5)
                   for c in range(5) if 1 <= r + e + c <= 4)
KINDS = ("DFA_SCAN", "DFA_HAT", "HYB_PF", "VM_ATTEMPT", "DFA_ATTEMPT")
FORMS = ("V1", "W64")
LAYERS = ("OFF", "W16", "W32")


def synthetic_rows(saving, xover, block, every=False):
    rows = []
    for f in FORMS:
        for sh in ALL_SHAPES + ("r2",):
            rows.append(row("kit.saving.%s.WALK.%s" % (f, sh), "ratio", saving, "synthetic", "synthetic"))
    rows.append(row("kit.eps.streamed.slope", "ratio", 0.01, "synthetic", "synthetic"))
    for f in FORMS:
        for k in KINDS:
            rows.append(row("kit.xover.%s.WALK.%s" % (f, k), "bytes", xover, "synthetic", "synthetic"))
    rows.append(row("kit.block.W64", "bytes", block, "synthetic", "synthetic"))
    if every:
        for f in ("V1", "W64"):
            for k in KINDS:
                rows.append(row("kit.gstar.%s.%s" % (f, k), "bytes", 8, "synthetic", "synthetic"))
        for k in KINDS:
            rows.append(row("kit.lstar.W64.%s" % k, "bytes", 128, "synthetic", "synthetic"))
            rows.append(row("kit.g8.W64.%s" % k, "bytes", 8, "synthetic", "synthetic"))
        rows.append(row("kit.h3a", "bytes", 16, "synthetic", "synthetic"))
        rows.append(row("kit.h3b", "bytes", 64, "synthetic", "synthetic"))
        # the pay rule's operands (PROVISIONAL keys), a dispatch that pays
        for k in KINDS:
            for alt, p in (("V1", "WALK"), ("W64", "WALK"), ("W64", "V1")):
                for n in (8, 32):
                    rows.append(row("kit.delta.%s.%s.%s.n%d" % (alt, p, k, n), "walkbytes", 20,
                                    "synthetic", "synthetic"))
                    rows.append(row("kit.dfloor.%s.%s.%s.n%d" % (alt, p, k, n), "walkbytes", 1,
                                    "synthetic", "synthetic"))
            for ly in LAYERS:
                for nf in (2, 3):
                    rows.append(row("kit.cdisp_call.%s.%s.%d" % (k, ly, nf), "walkbytes", 2,
                                    "synthetic", "synthetic"))
                    rows.append(row("kit.cfloor.%s.%s.%d" % (k, ly, nf), "walkbytes", 1,
                                    "synthetic", "synthetic"))
                    rows.append(row("kit.cdisp_use.%s.%s.%d" % (k, ly, nf), "walkbytes", 0,
                                    "synthetic", "synthetic"))
                    rows.append(row("kit.ufloor.%s.%s.%d" % (k, ly, nf), "walkbytes", 0,
                                    "synthetic", "synthetic"))
            for f in ("WALK", "V1", "W64"):
                rows.append(row("kit.wfloor.%s.%s" % (f, k), "walkbytes", 5, "synthetic", "synthetic"))
                for n in (36, 64, 128, xover if isinstance(xover, int) else 0):
                    rows.append(row("kit.ffloor.%s.%s.n%d" % (f, k, n), "walkbytes", 5,
                                    "synthetic", "synthetic"))
    return rows


def render(set_id, tier, method, cards_file, rows, label):
    seen = set()
    uniq = []
    for r in rows:                       # a key once (the every-key set may repeat one)
        if r["key"] not in seen:
            seen.add(r["key"])
            uniq.append(r)
    rows = sorted(uniq, key=lambda r: r["key"].encode())
    out = ["# memfn measurement set (spec: docs/design/measure_sets.md §1.2; "
           "docs/spec/measures.md lands at M0)",
           "# " + label,
           "# GENERATED by memfn/data/sets/generate.py; do not edit.",
           "#section header", "#key\tvalue"]
    hdr = [("format", "1"), ("id", set_id), ("rev", "1"), ("class", "x86_64-avx2/zen4"),
           ("isa", "x86-64-v3 avx2 sse4.2 popcnt bmi2"), ("tier", tier), ("composite", "0"),
           ("members", ""), ("unit_key", "kit.beta.WALK.DFA_SCAN.r1e0c0"), ("method", method),
           ("run", "slot grid1, 2026-10-13" if tier == "scratch" else "-"),
           ("box", "AMD Ryzen 7 7700X, CPU 14" if tier == "scratch" else "-"),
           ("compiler", "gcc 15.2.0 -O2" if tier == "scratch" else "-"),
           ("code_commit", "540649453" if tier == "scratch" else "-"),
           ("counters", "skipped:not-taken"), ("partial", "0"),
           ("rows", str(len(rows))), ("values_digest", fnv_digest(rows))]
    out += ["%s\t%s" % kv for kv in hdr]
    out.append("#section cards")
    with open(os.path.join(HERE, "..", "cards", cards_file)) as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if ln.startswith("#owner") or (ln and not ln.startswith("#")):
                out.append(ln)
    out.append("#section rows")
    out.append("#key\tunit\tvalue_e6\tabs_ns_e6\tnoise_e6\tn\tstatus\tderivation\tinputs\tdeps\ttags\tsource")
    for r in rows:
        out.append("\t".join((r["key"], r["unit"], str(r["value_e6"]), r["abs_ns_e6"], "-", "-",
                              r["status"], r["derivation"], r["inputs"], "-", "-", r["source"])))
    out.append("#section cells")
    out.append("#cell\tgroup\tarm\tlength\tlaunch\tround\tns_e6")
    return "\n".join(out) + "\n"


def main():
    check = "--check" in sys.argv[1:]
    files = {
        "kit-interim-grid1.tsv": render(
            "kit-interim-grid1", "scratch", "kit-grid@1", "kit-grid.tsv", interim_rows(),
            "kit-private interim set (pre-[MEASURE-SET]); format owner pcrec (regime_eval.md "
            "Q-REVAL-10). A TEST INPUT: no compile reads it but through the harness lever"),
        "synthetic-all-walk.tsv": render(
            "synthetic-all-walk", "synthetic", "kit-synthetic@1", "kit-synthetic.tsv",
            synthetic_rows(0.0, 1000000000, 64), "synthetic extreme: all-walk (r17b_prime.md §8.2)"),
        "synthetic-all-v1.tsv": render(
            "synthetic-all-v1", "synthetic", "kit-synthetic@1", "kit-synthetic.tsv",
            synthetic_rows(0.5, 0, 64), "synthetic extreme: all-v1 (r17b_prime.md §8.2)"),
        "synthetic-all-wide.tsv": render(
            "synthetic-all-wide", "synthetic", "kit-synthetic@1", "kit-synthetic.tsv",
            synthetic_rows(0.5, 0, 0), "synthetic extreme: all-wide (r17b_prime.md §8.2)"),
        "synthetic-every-key.tsv": render(
            "synthetic-every-key", "synthetic", "kit-synthetic@1", "kit-synthetic.tsv",
            synthetic_rows(0.5, 36, 64, every=True),
            "synthetic: every key a finder row or its pay rule can read (R-MS1, R-MS4; B4's "
            "every-derivable-key set)"),
    }
    bad = 0
    for name, text in files.items():
        path = os.path.join(HERE, name)
        if check:
            have = open(path).read() if os.path.exists(path) else None
            if have != text:
                print("generate.py --check: %s is stale or missing" % name)
                bad = 1
        else:
            with open(path, "w") as fh:
                fh.write(text)
    if check and not bad:
        print("generate.py --check: %d set files current" % len(files))
    return bad


if __name__ == "__main__":
    sys.exit(main())

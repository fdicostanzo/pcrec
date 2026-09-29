#!/usr/bin/env python3
"""eng_look_growth.py PCREC OUTDIR -- [ENG-LOOK] step 0 driver (plan.md's
eee1d36a wording): over the lookaround census population
(shapes_9399d927.tsv), the FIXED-LENGTH k=2-4 lookarounds, with the state
growth a product construction (`docs/dev/plan.md` [ENG-LOOK]'s own
mechanism: the body's Sigma*L/reverse(L)Sigma* recognizer folded into the
main automaton) would cost, measured per pattern:

  n_before = live reachable states of pcrec's OWN compiled DFA for the
             pattern with EVERY lookaround occurrence erased (--engine=dfa
             --no-captures --features all; a REAL compile, not a model) --
             the FORWARD machine for a lookbehind occurrence, the REVERSE
             machine for a lookahead one (plan.md's own pairing: lookbehind
             is a property of the forward-consumed prefix, lookahead of the
             reverse scan).
  n_body   = states of this module's own Sigma*L (lookbehind) or
             reverse(L)Sigma* (lookahead) recognizer for JUST the target
             occurrence's body (lac_engine.build_ends_with_dfa /
             build_starts_with_dfa_reversed) -- REAL, from a from-scratch
             subset construction, not estimated.
  n_after  = live reachable states of the EXACT product of the two REAL
             automata above (lac_engine.product_reachable, a BFS over live
             pairs -- exact reachability, not the |A|x|B| upper bound).

LOOKAHEAD gets a SECOND measurement, added after the first run surfaced a
methodological problem (see eng_look_census.md S3): pcrec's REVERSE
machine only walks the MATCHED span end-to-start, never the lookahead's
own body (past the match end, zero-width) -- so a product against it
(the brief's literal "reverse(L)Sigma* in the reverse machine" spec)
measures a machine that structurally never traverses the asserted text,
and reads artificially flat. plan.md's OWN ENG-LOOK mechanism text says
bounded lookahead folds into the FORWARD pass as a "k-byte delayed
acceptance" instead -- lac_engine.build_delayed_accept_dfa (the body's
own verify-next-k-bytes automaton, no Sigma* search prefix) composed
against the FORWARD erased-pattern machine. Both are reported for every
lookahead occurrence, labeled, so a reader sees the discrepancy rather
than one silently-chosen number.

MODEL, stated plainly: n_before erases ALL of a pattern's lookaround
occurrences (not just the target one) to get a single clean DFA baseline,
then adds back only the TARGET occurrence's product -- the marginal cost
of folding in ONE bounded lookaround, holding any others erased. A
multi-occurrence pattern's real shipped state growth (were every
occurrence folded) is not this script's question and is not reported.
BYTE ENCODING ONLY (confirmed 98/98 byte, 0 caseless before writing this).
A body atom lac_engine cannot resolve (UNRESOLVED) makes the OCCURRENCE
UNRESOLVED, not the count silently wrong -- reported separately, no body
DFA guessed.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import lac_engine as L
import shape_classify as sc

PCREC, OUTDIR = sys.argv[1:3]
CENSUS_TSV = os.path.join(os.path.dirname(__file__), "shapes_9399d927.tsv")


def load_rows():
    rows = []
    with open(CENSUS_TSV, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            v = line.rstrip("\n").split("\t")
            rows.append(dict(zip(header, v)))
    return rows


def compile_erased(pattern_text, enc):
    """Compiles pattern_text (str) with --engine=dfa --no-captures
    --features all. Returns (ok, c_source_or_stderr)."""
    with tempfile.TemporaryDirectory() as td:
        out_c = os.path.join(td, "out.c")
        cmd = [PCREC, "--engine=dfa", "--no-captures", "--features", "all",
               "-e", enc, "-o", out_c, "--pattern", pattern_text]
        try:
            r = subprocess.run(["timeout", "10"] + cmd, capture_output=True, text=True)
        except Exception as e:
            return False, str(e)
        if r.returncode != 0:
            return False, r.stderr.strip()
        with open(out_c) as f:
            return True, f.read()


def main():
    rows = load_rows()
    targets = [r for r in rows if r.get("ks") in ("2", "3", "4")]
    print("candidate rows (ks in 2,3,4): %d" % len(targets), file=sys.stderr)

    results = []
    skipped = []
    for r in targets:
        rid = r["id"]
        enc = r["enc"] or "byte"
        pat_text = r["pattern"]
        pat_bytes = pat_text.encode("utf-8", "surrogateescape")
        occs = sc.classify_pattern(pat_bytes)
        if not occs:
            skipped.append((rid, "reparse found no occurrences"))
            continue
        b_occs = [o for o in occs if o.get("shape") == "b" and o.get("k") in (2, 3, 4)]
        if not b_occs:
            skipped.append((rid, "reparse: no k=2-4 shape-b occurrence (census/reparse drift)"))
            continue
        erased = L.erase_occurrences(pat_bytes, occs)
        erased_text = erased.decode("utf-8", "surrogateescape")
        if not erased_text:
            skipped.append((rid, "erased pattern is empty"))
            continue
        ok, src_or_err = compile_erased(erased_text, enc)
        if not ok:
            skipped.append((rid, "erased-pattern compile refused: %s" % src_or_err[:160]))
            continue
        tables = L.parse_pcrec_tables(src_or_err)
        for occ in b_occs:
            k = occ["k"]
            kind = occ["kind"]
            branches, resolved = L.try_parse_body(occ["body"])
            if not resolved:
                results.append(dict(id=rid, kind=kind, k=k, method="",
                                     n_before=None, n_body=None, n_after=None,
                                     resolved=False, upper_bound=None,
                                     note="body atom unresolved: %r" % occ["body"]))
                continue

            if kind == "lookbehind":
                methods = [("forward_sigma_star", "forward")]
            else:
                methods = [("reverse_sigma_star_brief", "reverse"),
                           ("forward_delayed_accept", "forward")]

            for method, which in methods:
                if which not in tables:
                    skipped.append((rid, "erased pattern has no %s machine (routed elsewhere)" % which))
                    continue
                mach = tables[which]
                n_before = len(L.live_reachable_states(mach))
                if method == "forward_sigma_star":
                    b_trans, b_start, b_accept = L.build_ends_with_dfa(branches)
                elif method == "reverse_sigma_star_brief":
                    b_trans, b_start, b_accept = L.build_starts_with_dfa_reversed(branches)
                else:
                    b_trans, b_start, b_accept = L.build_delayed_accept_dfa(branches)
                n_body = len(L.bfs_reachable(b_trans, b_start)) if method != "forward_delayed_accept" \
                    else len(b_trans)
                product = L.product_reachable(mach["transitions"], mach["start"], mach["dead"],
                                               b_trans, b_start)
                n_after = len(product)
                results.append(dict(id=rid, kind=kind, k=k, method=method, n_before=n_before,
                                     n_body=n_body, n_after=n_after, resolved=True,
                                     upper_bound=n_before * n_body, note=""))

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "eng_look_growth.tsv"), "w") as f:
        f.write("id\tkind\tk\tmethod\tn_before\tn_body\tn_after\tupper_bound\tresolved\tnote\n")
        for r in results:
            f.write("\t".join(str(r.get(c, "")) for c in
                     ("id", "kind", "k", "method", "n_before", "n_body", "n_after", "upper_bound", "resolved", "note")) + "\n")
    with open(os.path.join(OUTDIR, "eng_look_skipped.tsv"), "w") as f:
        f.write("id\treason\n")
        for rid, reason in skipped:
            f.write("%s\t%s\n" % (rid, reason))

    resolved_rows = [r for r in results if r["resolved"]]
    print("\n== results ==", file=sys.stderr)
    print("total candidate occurrences: %d, resolved: %d, unresolved: %d, skipped(pattern-level): %d"
          % (len(results), len(resolved_rows), len(results) - len(resolved_rows), len(skipped)), file=sys.stderr)
    if resolved_rows:
        ratios = [r["n_after"] / r["n_before"] for r in resolved_rows if r["n_before"]]
        growths = [r["n_after"] - r["n_before"] for r in resolved_rows]
        print("n_before: min=%d max=%d mean=%.1f" % (
            min(r["n_before"] for r in resolved_rows), max(r["n_before"] for r in resolved_rows),
            sum(r["n_before"] for r in resolved_rows) / len(resolved_rows)), file=sys.stderr)
        print("n_after:  min=%d max=%d mean=%.1f" % (
            min(r["n_after"] for r in resolved_rows), max(r["n_after"] for r in resolved_rows),
            sum(r["n_after"] for r in resolved_rows) / len(resolved_rows)), file=sys.stderr)
        print("growth (n_after-n_before): min=%d max=%d mean=%.1f" % (
            min(growths), max(growths), sum(growths) / len(growths)), file=sys.stderr)
        print("ratio n_after/n_before: min=%.2f max=%.2f mean=%.2f" % (
            min(ratios), max(ratios), sum(ratios) / len(ratios)), file=sys.stderr)
        by_k = {}
        for r in resolved_rows:
            by_k.setdefault(r["k"], []).append(r)
        for k in sorted(by_k):
            rs = by_k[k]
            print("  k=%s n=%d mean_before=%.1f mean_after=%.1f mean_growth=%.1f" % (
                k, len(rs), sum(x["n_before"] for x in rs) / len(rs),
                sum(x["n_after"] for x in rs) / len(rs),
                sum(x["n_after"] - x["n_before"] for x in rs) / len(rs)), file=sys.stderr)
        by_dir = {}
        for r in resolved_rows:
            by_dir.setdefault(r["kind"], []).append(r)
        for kind in sorted(by_dir):
            rs = by_dir[kind]
            print("  %s n=%d mean_before=%.1f mean_after=%.1f" % (
                kind, len(rs), sum(x["n_before"] for x in rs) / len(rs),
                sum(x["n_after"] for x in rs) / len(rs)), file=sys.stderr)


if __name__ == "__main__":
    main()

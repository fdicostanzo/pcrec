#!/usr/bin/env python3
"""docs/design/dec_fallback/oracle_sweep.py -- [DEC-FALLBACK] B2: THE
BOTH-DERIVATIONS ORACLE over the full corpus mirror, in BOTH ORDERS
(dec_fallback.md §4.2 B2, §4.3 item 5; [START-TABLE] C2's shape).

For every limit variant (emit_sweep's VARIANTS) build TWO trace compilers of
one revision from `git archive`: the default trace build (today's derivation
asks first) and `-DPCREC_CAND_NEW_FIRST` (the new table asks first). Compile
row_reach's population (every distinct corpus block plus
reach/witnesses.tsv) under the prototype's 14 arms with both, and again with
`--emit-ir` (the listing's token site, which no `-o -` compile reaches).

WHAT IT FAILS ON (exit 1):
  - any `CANDORACLE` line, or a compile that died by a signal (the oracle
    aborts on a difference): the old derivation and the table disagreed;
  - the two orders' stdout or rc differ on any compile (an ask's side effect
    moved an artifact or a listing; the trace-vs-default byte identity of the
    default order is emit_sweep --trace's, not this script's);
  - K35: a checked SITE (admit, admit-listing, gate, stwhy, attrib, pfwhy)
    with no `CANDFIT` hit in an order, or a population below row_reach's
    floor. B2's `arrival` and `note` sites retired at B3 (decfbB3), which
    deleted their old side (the five tests and the `dropped_*` flags); a rev
    before B3 still prints them, and an extra site fails nothing.

It is a FILTER test: the oracle shares every predicate with its subject (the
note says so). The hits table (OUT/hits.tsv: order variant arm site row n)
shows which rows the population reached.

usage: oracle_sweep.py [--rev REV] [--variants a,b] [--arms a,b] [--stride N]
                       [--jobs N] [--out DIR]
Exit 0 clean, 1 a check failed, 2 a build failure.
"""
import argparse, collections, importlib.util, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import emit_sweep                                   # noqa: E402  VARIANTS, build_from_rev

_spec = importlib.util.spec_from_file_location("reach", os.path.join(HERE, "reach/reach.py"))
reach = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(reach)
_spec2 = importlib.util.spec_from_file_location("row_reach", os.path.join(HERE, "row_reach.py"))
row_reach = importlib.util.module_from_spec(_spec2); _spec2.loader.exec_module(row_reach)

ORDERS = {"old": "", "new": "-DPCREC_CAND_NEW_FIRST"}
SITES = ("admit", "admit-listing", "gate", "stwhy", "attrib", "pfwhy")
# arms whose --emit-ir run is skipped: the listing refuses a DFA engine and
# takes no --emit-facts.
NO_IR_ARMS = ("dfa", "facts")


def log(m):
    print(m, file=sys.stderr, flush=True)


def ir_argv(cmd):
    """The same compile as an `--emit-ir` listing (no `-o -`)."""
    out, skip = [], False
    for x in cmd:
        if skip:
            skip = False
            continue
        if x == b"-o":
            skip = True
            continue
        out.append(x)
    out.insert(1, b"--emit-ir")
    return out


def run_one(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", b"", [], []
    err = r.stderr.decode("utf-8", "replace").split("\n")
    oracle = [ln for ln in err if ln.startswith("CANDORACLE\t")]
    hits = [tuple(ln.split("\t")[1:3]) for ln in err if ln.startswith("CANDFIT\t")]
    return r.returncode, r.stdout, oracle, hits


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--variants", default=",".join(emit_sweep.VARIANTS))
    ap.add_argument("--arms", default=",".join(reach.ARMS))
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", default=os.path.join(ROOT, "build/oracle_sweep"))
    a = ap.parse_args()
    variants, arms = a.variants.split(","), a.arms.split(",")
    for v in variants:
        if v not in emit_sweep.VARIANTS:
            ap.error(f"unknown variant {v!r}")
    for x in arms:
        if x not in reach.ARMS:
            ap.error(f"unknown arm {x!r}")
    os.makedirs(a.out, exist_ok=True)
    cases = reach.corpus_cases(ROOT)[::a.stride] + reach.witness_cases(ROOT)
    log(f"[oracle_sweep] {a.rev}: population {len(cases)} (stride {a.stride})")
    fails, hits = [], collections.Counter()
    ncomp = collections.Counter()
    for v in variants:
        bins = {}
        for o, extra in ORDERS.items():
            cf = " ".join(x for x in (emit_sweep.TRACE_CFLAGS, extra, emit_sweep.VARIANTS[v]) if x)
            try:
                bins[o], _ = emit_sweep.build_from_rev(ROOT, a.rev, a.out, "gcc",
                                                       f"oracle-{o}-{v}", cflags=cf)
            except Exception as e:      # noqa: BLE001  a build failure is exit 2
                log(f"[oracle_sweep] BUILD FAILED {o} {v}: {e}")
                sys.exit(2)
        for arm in arms:
            if v == "lowthr" and arm not in row_reach.LOWTHR_ARMS:
                continue
            log(f"[oracle_sweep] {v} {arm} ...")

            def one(case):
                src, key = case
                out = []
                base = {o: reach.argv(b, key, arm, src == "corpus") for o, b in bins.items()}
                kinds = [("c", lambda c: c)]
                if arm not in NO_IR_ARMS:
                    kinds.append(("ir", ir_argv))
                for kind, mk in kinds:
                    res = {o: run_one(mk(cmd)) for o, cmd in base.items()}
                    out.append((src, key, kind, res))
                return out

            with ThreadPoolExecutor(max_workers=a.jobs) as ex:
                for batch in ex.map(one, cases):
                    for src, key, kind, res in batch:
                        tag = f"{v} {arm} {kind} {src} {key[0][:60]!r}"
                        for o, (rc, _out, orc, hs) in res.items():
                            ncomp[o] += 1
                            if orc:
                                fails.append(f"ORACLE {o} {tag}: {orc[0]}")
                            if rc == "TIMEOUT":
                                fails.append(f"TIMEOUT {o} {tag}")
                            elif rc < 0 or rc >= 128:
                                fails.append(f"SIGNAL {o} {tag}: rc {rc}")
                            for site, row in hs:
                                hits[(o, v, arm, site, row)] += 1
                        (rca, outa, _, _), (rcb, outb, _, _) = res["old"], res["new"]
                        if rca != rcb or outa != outb:
                            fails.append(f"ORDER DIFFERS {tag}: rc {rca}/{rcb}, "
                                         f"stdout {'same' if outa == outb else 'differs'}")
    full = a.stride == 1
    if full and len(cases) < row_reach.POPULATION_FLOOR:
        fails.append(f"POPULATION FLOOR: {len(cases)} < {row_reach.POPULATION_FLOOR}")
    site_tot = collections.Counter()
    for (o, _v, _arm, site, _row), n in hits.items():
        site_tot[(o, site)] += n
    for o in ORDERS:
        for site in SITES:
            if not site_tot[(o, site)]:
                fails.append(f"K35: site {site} has NO CANDFIT hit in order {o}")
    with open(os.path.join(a.out, "hits.tsv"), "w") as fh:
        fh.write("order\tvariant\tarm\tsite\trow\tn\n")
        for k, n in sorted(hits.items()):
            fh.write("\t".join(k) + f"\t{n}\n")
    rows = collections.defaultdict(collections.Counter)
    for (o, _v, _arm, site, row), n in hits.items():
        rows[(o, site)][row] += n
    print(f"population: {len(cases)} cases x {len(variants)} variants x arms; "
          f"compiles old {ncomp['old']} new {ncomp['new']}")
    for o in ORDERS:
        print(f"order {o}: " + " ".join(f"{s}={site_tot[(o, s)]}" for s in SITES))
        for site in SITES:
            print(f"  {site}: " + ", ".join(f"{r} {n}" for r, n in sorted(rows[(o, site)].items())))
    for ln in fails[:40]:
        print("  " + ln)
    if len(fails) > 40:
        print(f"  ... {len(fails) - 40} more")
    print(f"table: {os.path.join(a.out, 'hits.tsv')}")
    print("ORACLE_SWEEP: " + ("CLEAN" if not fails else f"FAILED ({len(fails)})"))
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()

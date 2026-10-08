#!/usr/bin/env python3
"""[NULLABLE-ANCH] STEP 0 -- the compile-side census (lane nullanch0,
MEASUREMENT ONLY: reads the built compiler, changes nothing under src/).

Population: every distinct `pattern`/`pattern-esc` line under tests/**/*.rxt
(corpus; byte encoding, --features all -- emit_sweep.py's own convention)
plus every pattern of pcrec-bench's published sets (read-only: bench/*/
export/*.rxt, bench/capability/patterns.rxt, bench/utf8/patterns.rxt).

Per pattern: the artifact stamps of a default `-p rx --features all`
compile (engine, ENGINE_SEL/WHY, VM_PREFILTER, VM_START, rungs, strategies,
possessify arms, REQ/END_WINDOW), the same compile under `--no-captures`
(the DFA arm the f2_rescue_split memo calls the search-filter), and
anch_probe's AST verdicts (nullable, empty-path mask set, dismissable,
nested, nullbody). For every pattern the DEFAULT compile declines on
nullability (ENGINE_SEL declined-nullable[-default]) a third call reads the
`--emit-ir` summary (rungs, possessify, the empty-iteration guard slot).

Usage: census.py PCREC_BIN PROBE_BIN BENCH_DIR OUT_DIR [JOBS]
Writes OUT_DIR/census_rows.tsv and prints the summary tables."""
import os, re, subprocess, sys, collections, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import emit_sweep as es   # decode_escape / encode_escape / list_source_patterns

KEYS = ["RX_ENGINE", "RX_ENGINE_SEL", "RX_ENGINE_WHY", "RX_VM_PREFILTER",
        "RX_VM_START", "RX_NCAPS", "RX_VM_RUNGS", "RX_VM_STRATS",
        "RX_VM_POSS_ARMS", "RX_VM_FRAMELESS", "RX_REQ_BYTE", "RX_REQ_RUN",
        "RX_END_WINDOW", "RX_VM_START_SCAN", "RX_VM_PRUNE_CEILING"]
DEF = re.compile(rb'^#define (RX_[A-Z0-9_]+) (.*)$', re.M)


def stamps(out):
    d = {}
    for m in DEF.finditer(out):
        k = m.group(1).decode()
        if k in KEYS and k not in d:
            d[k] = m.group(2).decode(errors="replace").strip().strip('"')
    return d


def compile_stamps(pcrec, pat, extra=()):
    argv = [pcrec, "-p", "rx", "--features", "all", *extra, "-o", "-", "--pattern", pat]
    r = subprocess.run(argv, capture_output=True, timeout=60)
    if r.returncode != 0:
        return None
    return stamps(r.stdout)


def ir_summary(pcrec, pat):
    argv = [pcrec, "--features", "all", "--engine=vm", "--emit-ir", "--pattern", pat]
    r = subprocess.run(argv, capture_output=True, timeout=60)
    if r.returncode != 0:
        return {}
    t = r.stdout.decode(errors="replace")
    d = {}
    for ln in t.splitlines():
        f = ln.split("\t")
        if len(f) >= 2 and f[0] in ("rungs", "strategies", "possessify", "prune-ceiling"):
            d[f[0]] = f[1]
        if len(f) >= 3 and f[0] == "guard" and f[1]:
            d["guard"] = "slot" + f[1]
    d["guard_loops"] = str(t.count("nullable body (empty-iteration guard)"))
    d.setdefault("guard", "none")
    return d


def population(bench):
    pats = {}   # pattern bytes -> list of (origin, name)
    files = es.find_files(ROOT, (".rxt",))
    for f in files:
        rel = os.path.relpath(f, ROOT)
        for kind, p in es.list_source_patterns(os.path.join(ROOT, "build", "pcrec"), f, 60):
            pats.setdefault(p, []).append(("corpus", rel))
    benchfiles = []
    for d in sorted(os.listdir(os.path.join(bench, "bench"))):
        for sub in ("export", "."):
            dd = os.path.join(bench, "bench", d, sub)
            if os.path.isdir(dd):
                for fn in sorted(os.listdir(dd)):
                    if fn.endswith(".rxt"):
                        benchfiles.append((d, os.path.join(dd, fn)))
    for d, f in benchfiles:
        r = subprocess.run([os.path.join(ROOT, "build", "pcrec"), "--list-source", f],
                           capture_output=True, timeout=60)
        for ln in r.stdout.decode("utf-8", "surrogateescape").splitlines():
            if ln.startswith("#") or not ln.strip():
                continue
            c = ln.split("\t")
            if len(c) < 9 or c[0] not in ("pattern", "pattern-esc"):
                continue
            pats.setdefault(es.decode_escape(c[4]), []).append(("bench", d + ":" + c[2] + ("[" + c[8] + "]" if c[8] else "")))
    return pats


def main():
    pcrec, probe, bench, out = sys.argv[1:5]
    jobs = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    os.makedirs(out, exist_ok=True)
    pats = population(bench)
    order = sorted(pats)
    print(f"distinct patterns: {len(order)} (corpus lines + bench)", file=sys.stderr)
    # the probe, one process over all patterns
    inp = "".join(f"{i}\t{es.encode_escape(p)}\n" for i, p in enumerate(order)).encode("utf-8", "surrogateescape")
    pr = subprocess.run([probe], input=inp, capture_output=True, timeout=600)
    probe_rows = {}
    for ln in pr.stdout.decode().splitlines():
        if ln.startswith("#"):
            continue
        f = ln.split("\t")
        probe_rows[int(f[0])] = f[1:]

    def job(i):
        p = order[i]
        ps = p.decode("utf-8", "surrogateescape")
        base = compile_stamps(pcrec, ps)
        nocap = compile_stamps(pcrec, ps, ("--no-captures",))
        ir = {}
        if base and base.get("RX_ENGINE_SEL", "").startswith("declined-nullable"):
            ir = ir_summary(pcrec, ps)
        return i, base, nocap, ir

    res = {}
    with cf.ThreadPoolExecutor(jobs) as ex:
        for i, base, nocap, ir in ex.map(job, range(len(order))):
            res[i] = (base, nocap, ir)

    cols = ["id", "origins", "pattern", "compiles", "engine", "sel", "why", "vm_prefilter",
            "vm_start", "ncaps", "rungs", "strats", "poss_arms", "frameless", "req_byte",
            "req_run", "end_window", "nc_engine", "nc_sel", "nc_prefilter",
            "probe_parse", "nullable", "masks", "dismissable", "nested", "nullbody", "xchk",
            "ir_rungs", "ir_strat", "ir_poss", "ir_guard", "ir_guard_loops"]
    with open(os.path.join(out, "census_rows.tsv"), "w", encoding="utf-8", errors="surrogateescape") as fh:
        fh.write("#" + "\t".join(cols) + "\n")
        for i, p in enumerate(order):
            base, nocap, ir = res[i]
            pr = probe_rows.get(i, [""] * 7)
            b = base or {}
            n = nocap or {}
            org = ";".join(sorted({f"{a}:{b_}" for a, b_ in pats[p]}))[:200]
            row = [str(i), org, es.encode_escape(p), "1" if base else "0",
                   b.get("RX_ENGINE", ""), b.get("RX_ENGINE_SEL", ""), b.get("RX_ENGINE_WHY", ""),
                   b.get("RX_VM_PREFILTER", ""), b.get("RX_VM_START", ""), b.get("RX_NCAPS", ""),
                   b.get("RX_VM_RUNGS", ""), b.get("RX_VM_STRATS", ""), b.get("RX_VM_POSS_ARMS", ""),
                   b.get("RX_VM_FRAMELESS", ""), b.get("RX_REQ_BYTE", ""), b.get("RX_REQ_RUN", ""),
                   b.get("RX_END_WINDOW", ""),
                   n.get("RX_ENGINE", ""), n.get("RX_ENGINE_SEL", ""), n.get("RX_VM_PREFILTER", ""),
                   *pr[:7],
                   ir.get("rungs", ""), ir.get("strategies", ""), ir.get("possessify", ""),
                   ir.get("guard", ""), ir.get("guard_loops", "")]
            fh.write("\t".join(x.replace("\t", " ").replace("\n", " ") for x in row) + "\n")
    print("wrote", os.path.join(out, "census_rows.tsv"), file=sys.stderr)


if __name__ == "__main__":
    main()

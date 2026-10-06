#!/usr/bin/env python3
"""docs/design/start_table/trace_experiment.py -- Frank's Q3 experiment
(D151 addendum 3; start_table.md §6 Q3): does a selection trace catch
selection changes the byte sweep misses, without false alarms on
selection-NEUTRAL commits?

Builds, from the scratch branch carrying the C0 PROTOTYPE hook
(scratch/stc0-trace: CANDTRACE records at today's walk sites), the PARENT
and one variant per PLANT below, every one with -DPCREC_CAND_TRACE; compiles
the distinct corpus patterns (emit_sweep.py's enumeration) under streams 1-2
with each; and compares every variant against the parent two ways:
  - BYTES: patterns whose emitted stdout moved (the byte sweep's verdict);
  - TRACE: scripts/trace_diff.py over the ordered per-pattern sequences, in
    three key modes -- `spec` (slot, route, row, site: the note's §3.3 item 5
    record), `func` (spec + the C function name: what a __func__ site gives)
    and `set` (spec fields, per pattern-arm SET: order and multiplicity
    ignored).
A DETECTION plant must be caught; a NEUTRAL plant must read clean.

Usage: trace_experiment.py SCRATCH_TREE OUTDIR [--jobs N] [--only NAME,..]
Writes OUTDIR/<variant>.tsv (trace streams), OUTDIR/results.tsv. Read-only
on SCRATCH_TREE (variants are `git archive`d into OUTDIR/src_<variant>).
"""
import argparse, concurrent.futures, os, re, subprocess, sys, tarfile, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import emit_sweep as es   # noqa: E402
import trace_diff as td   # noqa: E402

DFA = "src/gen/emit_dfa.c"

# (name, kind, description, [(file, old, new, count)]) -- every edit asserts
# its exact occurrence count (BOILERPLATE: patch harnesses assert counts).
PLANTS = [
    ("parent", "-", "the prototype itself", []),
    ("D1-row-swap", "detect", "dfa_pfs[]: rows run-pinned-bounded and run-pinned swapped", [
        (DFA, '''    { .c = { "run-pinned-bounded",  PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER, pf_run_bounded_applies },
      .emit_tables = pf_tables_ofs,  .emit_block = pf_block_ofs, .emit = pf_emit_ofs_bounded,
      .reseeds = true,  .run_term = true,  .scan = PF_SCAN_OFS  },
    { .c = { "run-pinned",          PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER, pf_run_applies         },
      .emit_tables = pf_tables_ofs,  .emit_block = pf_block_ofs, .emit = pf_emit_ofs,
      .reseeds = true,  .run_term = true,  .scan = PF_SCAN_OFS  },''',
         '''    { .c = { "run-pinned",          PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER, pf_run_applies         },
      .emit_tables = pf_tables_ofs,  .emit_block = pf_block_ofs, .emit = pf_emit_ofs,
      .reseeds = true,  .run_term = true,  .scan = PF_SCAN_OFS  },
    { .c = { "run-pinned-bounded",  PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER, pf_run_bounded_applies },
      .emit_tables = pf_tables_ofs,  .emit_block = pf_block_ofs, .emit = pf_emit_ofs_bounded,
      .reseeds = true,  .run_term = true,  .scan = PF_SCAN_OFS  },''', 1)]),
    ("D2a-pred-flip", "detect", "req_admits[]: G1 `dominated` predicate negated", [
        (DFA, '''    { { "dominated",   0,                      req_dominated_applies   }, REQ_ADMIT_DOMINATED,''',
         '''    { { "dominated",   0,                      req_dominated_flipped   }, REQ_ADMIT_DOMINATED,''', 1),
        (DFA, '''static const ReqAdmitRow req_admits[] = {''',
         '''static bool req_dominated_flipped(const DfaSel *s) { return !req_dominated_applies(s); }
static const ReqAdmitRow req_admits[] = {''', 1)]),
    ("D2b-pred-boundary", "detect", "pf_vm_start_applies: `n >= 256` -> `n > 256` (a boundary flip)", [
        (DFA, "    if (n >= 256) return false;\n    vm_start_assert_starts(cx, ss);",
         "    if (n > 256) return false;\n    vm_start_assert_starts(cx, ss);", 1)]),
    ("D3-route-miskey", "detect", "dfa_pf_of builds its selection on CAND_ROUTE_VM", [
        (DFA, '''    DfaSel s = { .cx = cx, .d = &cx->job->dfa, .us = us, .forward = true, .st = -1,
                 .route = CAND_ROUTE_DFA, .ss = pcrec_fact_start_set(cx) };
    const DfaPf *pf = DFA_SELECT_ROUTED(DfaPf, dfa_pfs, &s, cx->opt->flags);
    PCREC_CAND_TRACE_REC("NEXT", CAND_ROUTE_NAME(s.route), pf->c.name, "pf-of");''',
         '''    DfaSel s = { .cx = cx, .d = &cx->job->dfa, .us = us, .forward = true, .st = -1,
                 .route = CAND_ROUTE_VM, .ss = pcrec_fact_start_set(cx) };
    const DfaPf *pf = DFA_SELECT_ROUTED(DfaPf, dfa_pfs, &s, cx->opt->flags);
    PCREC_CAND_TRACE_REC("NEXT", CAND_ROUTE_NAME(s.route), pf->c.name, "pf-of");''', 1)]),
    ("D4-bytes-identical", "detect",
     "pcrec_dfa_scan_state_written walks dfa_pfs[] with -fno-run-prefilter's bit forced: "
     "run-pinned -> offset-set, both `reseeds`, so the answer (and every byte) is unchanged", [
        (DFA, '''    const DfaPf *pf = DFA_SELECT_ROUTED(DfaPf, dfa_pfs, &s, cx->opt->flags);
    PCREC_CAND_TRACE_REC("NEXT", CAND_ROUTE_NAME(s.route), pf->c.name, "scan-state");''',
         '''    const DfaPf *pf = DFA_SELECT_ROUTED(DfaPf, dfa_pfs, &s, cx->opt->flags | PCREC_NO_RUN_PREFILTER);
    PCREC_CAND_TRACE_REC("NEXT", CAND_ROUTE_NAME(s.route), pf->c.name, "scan-state");''', 1)]),
    ("N1-rename", "neutral", "rename dfa_pf_of -> dfa_prefilter_of and req_use -> req_use_of (every occurrence)", [
        (DFA, "dfa_pf_of(", "dfa_prefilter_of(", None),
        (DFA, "req_use(", "req_use_of(", None)]),
    ("N2-move", "neutral", "move req_use's definition to the end of emit_dfa.c (its prototype already exists)", [
        (DFA, "MOVE:req_use", None, None)]),
    ("N3-reformat", "neutral", "reformat the source of dfa_search_start_of and req_admit (line breaks/spacing; same tokens)", [
        (DFA, '''    const DfaSearchStart *ss = DFA_SELECT(DfaSearchStart, dfa_search_starts, &s, cx->opt->flags);''',
         '''    const DfaSearchStart *ss =
        DFA_SELECT(DfaSearchStart, dfa_search_starts, &s,
                   cx->opt->flags);''', 1),
        (DFA, '''    const ReqAdmitRow *r = DFA_SELECT(ReqAdmitRow, req_admits, &s, cx->opt->flags);''',
         '''    const ReqAdmitRow *r =
        DFA_SELECT(ReqAdmitRow,
                   req_admits, &s, cx->opt->flags);''', 1)]),
    ("N4-extra-ask", "neutral-beyond-bar",
     "a reader asks FIRST once more (req_handoff_stamp re-asks req_use): selection unchanged, ask multiplicity +1", [
        (DFA, '''    if (req_use(cx) != REQ_USE_HANDOFF) return "none";''',
         '''    (void)req_use(cx);
    if (req_use(cx) != REQ_USE_HANDOFF) return "none";''', 1)]),
]


def move_fn(s, name):
    """Cut `static ReqUse NAME(Ctx *cx)\n{ ... \n}\n` and append it at EOF."""
    m = re.search(r"\nstatic ReqUse " + name + r"\(Ctx \*cx\)\n\{.*?\n\}\n", s, re.S)
    assert m, name
    return s[:m.start()] + "\n" + s[m.end():] + m.group(0)


def build(scratch_tree, out, name, edits, cc, jobs):
    src = os.path.join(out, "src_" + name)
    binp = os.path.join(src, "build", "pcrec")
    if os.path.exists(binp):
        return binp
    os.makedirs(src, exist_ok=True)
    p = subprocess.Popen(["git", "-C", scratch_tree, "archive", "HEAD"], stdout=subprocess.PIPE)
    with tarfile.open(fileobj=p.stdout, mode="r|") as tf:
        tf.extractall(src)
    p.wait()
    for f, old, new, count in edits:
        path = os.path.join(src, f)
        s = open(path).read()
        if old.startswith("MOVE:"):
            s = move_fn(s, old[5:])
        else:
            n = s.count(old)
            assert n and (count is None or n == count), (name, old[:60], n)
            s = s.replace(old, new)
        open(path, "w").write(s)
    r = subprocess.run(["make", f"-j{jobs}", f"CC={cc}", f"CFLAGS={es.TRACE_CFLAGS}"],
                       cwd=src, capture_output=True, timeout=1200)
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode()[-3000:])
        raise SystemExit(f"build {name} failed")
    return binp


def run_variant(binp, pats, jobs, path):
    """{(idx, arm): sha256(stdout)}; writes the trace stream to path."""
    def job(item):
        idx, p = item
        out = []
        for arm, eng in es.ARM_STREAMS.items():
            ok, o, err = es.compile_stream_c(binp, p, 60, engine=eng, want_err=True)
            out.append((arm, es.sha(o), es.trace_records(err)))
        return idx, out
    hashes = {}
    with open(path, "w") as fh, concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        fh.write("idx\tarm\tseq\trecord\n")
        for idx, out in ex.map(job, list(enumerate(pats))):
            for arm, h, recs in out:
                hashes[(idx, arm)] = h
                for seq, rec in enumerate(recs):
                    fh.write(f"{idx}\t{arm}\t{seq}\t{rec}\n")
    return hashes


def set_movers(a, b, keys):
    n = 0
    for k in set(a) | set(b):
        if {td.project(r, keys) for r in a.get(k, [])} != {td.project(r, keys) for r in b.get(k, [])}:
            n += 1
    return n


def seq_movers(a, b, keys):
    n = 0
    for k in set(a) | set(b):
        if [td.project(r, keys) for r in a.get(k, [])] != [td.project(r, keys) for r in b.get(k, [])]:
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch_tree"); ap.add_argument("out")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--only")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cc = es.resolve_cc(a.scratch_tree)
    plants = [p for p in PLANTS if not a.only or p[0] == "parent" or p[0] in a.only.split(",")]
    bins = {}
    for name, kind, desc, edits in plants:
        t = time.time()
        bins[name] = build(a.scratch_tree, a.out, name, edits, cc, a.jobs)
        print(f"built {name} ({time.time() - t:.0f}s)", flush=True)
    pats = es.distinct_patterns(es.enumerate_corpus(bins["parent"], a.scratch_tree, 30))
    print(f"population: {len(pats)} distinct patterns x {len(es.ARM_STREAMS)} streams", flush=True)
    hashes, traces = {}, {}
    for name, *_ in plants:
        t = time.time()
        path = os.path.join(a.out, name + ".tsv")
        hashes[name] = run_variant(bins[name], pats, a.jobs, path)
        traces[name] = td.load(path)
        print(f"ran {name} ({time.time() - t:.0f}s)", flush=True)
    spec = ["slot", "route", "row", "site"]
    rows = []
    P = traces["parent"]
    recs = {arm: sum(len(v) for k, v in P.items() if k[1] == arm) for arm in es.ARM_STREAMS}
    print(f"parent records per arm: {recs}")
    for name, kind, desc, _ in plants[1:]:
        V = traces[name]
        bytes_moved = sum(1 for k in hashes["parent"] if hashes["parent"][k] != hashes[name].get(k))
        r = (name, kind, bytes_moved, seq_movers(P, V, spec), seq_movers(P, V, spec + ["func"]),
             set_movers(P, V, spec), desc)
        rows.append(r)
        print("\t".join(map(str, r[:6])), flush=True)
    with open(os.path.join(a.out, "results.tsv"), "w") as fh:
        fh.write("variant\tkind\tbyte_movers\ttrace_spec\ttrace_func\ttrace_set\tdescription\n")
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
        fh.write(f"# parent records per arm: {recs}; population {len(pats)} distinct x 2 streams\n")


if __name__ == "__main__":
    main()

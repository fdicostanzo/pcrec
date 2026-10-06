#!/usr/bin/env python3
"""[START-SET] STAGE 1's CENSUS: the D77 census re-run on the BUILT fact with
per-block options (D148; docs/design/startset.md §1 and §8 stage 1, review r4
sound-F4), and the stage-2/3 MOVER MANIFESTS generated from it (checks-F5).

What changed from r3's census (`../census.py`):
  * the start set is the SHIPPED `start_set` row of `--emit-facts`, never
    `fs_probe` (checks-F2: a probe rebuilding the pipeline prefix ignored the
    compile's `-i`/`--ucp`, sound-F4);
  * corpus blocks compile with THEIR OWN options and are deduplicated on
    (text, options), through tests/startset/startset_lib.py -- the population
    the stage-1 checks read, so the census and the checks cannot count two
    different corpora;
  * the DFA hat's set is T = S, admitted iff T ⊊ E (D148 addenda 1-2,
    Q-R1; rev 2's `S ∩ E*` was struck by the ss3 D6 panel's BLOCKER
    sound-F1, lane ssfix3), E read off the emitted tables;
  * (ssfix3, the panel's checks-m5) every compile carries `-fno-start-set`:
    the deny arm is today's emitter without either hat, so the census reads
    the plain row and the plain tables on ANY build, before or after the
    stage that builds a hat, and a regeneration never needs a frozen binary.

Populations and arms. BENCH: every pcrec-bench export (read-only), at the
bench's `pcrec-auto` flags (`--features all`, `-e utf8` on bench/utf8).
CORPUS: every block, its own options. Each at `auto` (its options) and `vm`
(its options with `--engine=vm` replacing any engine).

The two hats' predicates, as stage 2/3 will build them:
  V (VM hat, stage 2): RX_ENGINE "vm", RX_VM_PREFILTER "none", start_anchor
    "unanchored", start_set not nullable and fewer than 256 members. (The
    verbs/callouts conjunct is unreachable: every verb refuses at compile.)
  F (DFA hat, stage 3): a forward DFA scan RX_DFA_SCAN "unanchored", a SEEDED
    machine, the selected prefilter a plain row the new rows sit above
    (`memchr[-bounded]`, `byte-class[-bounded]`; offset/run rows win first),
    S necessary, and T = S a non-empty PROPER subset of E. The census also
    counts S ⊆ E* and |E*| == 256 (rev 2's claim, refuted by sound-F1: a
    byte of S can leave every seed where it is).

Env: PCREC (the stage-1 build), TREE (the pcrec checkout), BENCH, OUT, JOBS.
Writes OUT/census_s1.tsv, OUT/census_s1_summary.txt and, with MANIFESTS=dir,
the three mover manifests there.
"""
import concurrent.futures as cf, os, re, subprocess, sys, tempfile

E = os.environ
TREE = E["TREE"]
sys.path.insert(0, os.path.join(TREE, "tests", "startset"))
import startset_lib as L

PCREC, OUT = E["PCREC"], E.get("OUT", ".")
BENCH = E.get("BENCH", "/Users/fdicostanzo/pcrec-bench")
JOBS = int(E.get("JOBS", "6"))
SETS = {"capability": [], "syntax": [], "utf8": ["-e", "utf8"], "loglines": [],
        "bounded": [], "email": [], "altwide": [], "litrun": []}
PLAIN_PF = {"memchr", "memchr-bounded", "byte-class", "byte-class-bounded"}


def bench_pop():
    rows = []
    for sb, extra in SETS.items():
        d = os.path.join(BENCH, "bench", sb, "patterns")
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".rx"):
                rows.append({"id": "bench/%s/%s" % (sb, fn[:-3]), "kind": "bench",
                             "pattern": open(os.path.join(d, fn), "rb").read(),
                             "args": ["--features", "all", *extra]})
    return rows


def vm_args(args):
    out, skip = [], False
    for a in args:
        if a.startswith("--engine="): continue
        out.append(a)
    return out + ["--engine=vm"]


def arm(b, args, td, want_c):
    args = [*args, "-fno-start-set"]
    try:
        r = subprocess.run([PCREC, *args, "--emit-facts", "--pattern", b["pattern"]],
                           capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    if r.returncode:
        return {"status": "refused"}
    fct, dec = L.facts(r.stdout.decode("utf-8", "replace"))
    rec = {"status": "ok", "engine": dec.get("RX_ENGINE", "").strip('"'),
           "vmpf": dec.get("RX_VM_PREFILTER", "").strip('"'),
           "scan": dec.get("RX_DFA_SCAN", "").strip('"'),
           "dfapf": dec.get("RX_DFA_PREFILTER", "").strip('"'),
           "sanch": fct.get("start_anchor", {}).get("value", ""),
           "nullable": fct.get("nullable", {}).get("value", ""),
           "ss": fct.get("start_set", {}).get("value", "")}
    if want_c and rec["scan"]:
        o = os.path.join(td, "%x.c" % (abs(hash((b["id"], tuple(args)))) & 0xffffffffffff))
        try:
            c = subprocess.run([PCREC, *args, "-p", "rx", "-o", o, "--pattern", b["pattern"]],
                               capture_output=True, timeout=300)
            if c.returncode == 0:
                rec["m"] = L.machine_sets(open(o, errors="replace").read())
        except subprocess.TimeoutExpired:
            pass
        for f in (o, o[:-2] + ".h"):
            try: os.remove(f)
            except OSError: pass
    return rec


def one(b, td):
    return arm(b, b["args"], td, True), arm(b, vm_args(b["args"]), td, False)


def vhat(r):
    if r["status"] != "ok" or not r["ss"]: return False
    nul, S = L.set_of(r["ss"])
    return (r["engine"] == "vm" and r["vmpf"] == "none" and r["sanch"] == "unanchored"
            and not nul and len(S) < 256)


def fhat(r):
    """(admitted, S within E*, |E*|==256, why) for the DFA hat (T = S)."""
    if r["status"] != "ok" or r["scan"] != "unanchored": return False, None, None, "route"
    m = r.get("m")
    if not m or m.get("status") != "ok": return False, None, None, "unread"
    if m["nseeds"] < 2: return False, None, None, "unseeded"
    if r["dfapf"] not in PLAIN_PF: return False, None, None, "row:" + (r["dfapf"] or "?")
    nul, S = L.set_of(r["ss"])
    if nul or len(S) >= 256: return False, None, None, "S-not-necessary"
    T = S
    ok = bool(T) and T < m["E"]
    return ok, S <= m["Estar"], len(m["Estar"]) == 256, "admit" if ok else "T-not-proper"


def main():
    corpus, cnt = L.corpus_blocks(PCREC, TREE)
    for b in corpus: b["kind"] = "corpus"
    pop = bench_pop() + corpus
    sys.stderr.write("population %d (bench %d, corpus %d)\n" % (len(pop), len(pop) - len(corpus), len(corpus)))
    with tempfile.TemporaryDirectory() as td, cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(lambda b: one(b, td), pop))
    lines, summ = [], {}
    manif = {"s2_vm_auto": [], "s2_vm_forced": [], "s3_dfa": []}

    def bump(k, kind):
        summ.setdefault(k, {"bench": 0, "corpus": 0})[kind] += 1

    for b, (a, v) in zip(pop, res):
        kind = b["kind"]
        bump("population", kind)
        if a["status"] != "ok":
            bump("auto refused", kind)
        if v["status"] != "ok":
            bump("vm refused", kind)
        f_ok, t_eq_s, estar_full, why = fhat(a)
        va, vv = vhat(a), vhat(v)
        if a["status"] == "ok":
            bump("auto route %s/%s" % (a["engine"], a["vmpf"] or a["scan"] or "-"), kind)
        if va:
            bump("V at auto (stage 2 movers)", kind); manif["s2_vm_auto"].append(b)
            if any(x.startswith("--engine=") for x in b["args"]):
                bump("V at auto: the block itself pins --engine", kind)
        if vv: bump("V under --engine=vm (stage 2 movers)", kind); manif["s2_vm_forced"].append(b)
        if a["status"] == "ok" and a["scan"] == "unanchored" and a.get("m", {}).get("status") == "ok" \
                and a["m"]["nseeds"] >= 2:
            bump("DFA scan, seeded", kind)
            bump("DFA scan, seeded, why %s" % why, kind)
            if estar_full is not None:
                bump("F-checked: |E*| == 256" if estar_full else "F-checked: |E*| < 256", kind)
        if f_ok:
            bump("F admitted (stage 3 movers)", kind); manif["s3_dfa"].append(b)
            bump("F admitted: S within E*" if t_eq_s else "F admitted: S not within E* (rev 2's T = S & E* would drop a start byte)", kind)
        lines.append("\t".join([kind, b["id"], " ".join(b["args"]), b["pattern"].hex(), a["status"],
                                a.get("engine", ""), a.get("vmpf", ""), a.get("scan", ""), a.get("dfapf", ""),
                                a.get("sanch", ""), a.get("nullable", ""), a.get("ss", ""), v["status"],
                                v.get("engine", ""), v.get("vmpf", ""), v.get("sanch", ""), v.get("ss", ""),
                                "1" if va else "0", "1" if vv else "0", why, "1" if f_ok else "0"]))
    cols = ["kind", "id", "options", "pattern_hex", "a_status", "a_engine", "a_vm_prefilter", "a_dfa_scan",
            "a_dfa_prefilter", "a_start_anchor", "a_nullable", "a_start_set", "v_status", "v_engine",
            "v_vm_prefilter", "v_start_anchor", "v_start_set", "V_auto", "V_vm", "F_why", "F_admit"]
    with open(os.path.join(OUT, "census_s1.tsv"), "w") as f:
        f.write("# [START-SET] stage-1 census (lane ssbuild01). Generated by census_s1.py; see its header.\n")
        f.write("\t".join(cols) + "\n" + "\n".join(lines) + "\n")
    with open(os.path.join(OUT, "census_s1_summary.txt"), "w") as f:
        f.write("[START-SET] stage-1 census, per-block options, the BUILT start_set fact.\n")
        f.write("corpus enumeration: %d .rxt files, %d pattern rows, %d NUL-bearing out, %d (text, options) duplicates\n"
                % (cnt["files"], cnt["rows"], cnt["nul"], cnt["dup"]))
        f.write("%-58s %8s %8s\n" % ("count", "bench", "corpus"))
        for k in sorted(summ):
            f.write("%-58s %8d %8d\n" % (k, summ[k]["bench"], summ[k]["corpus"]))
    md = E.get("MANIFESTS")
    if md:
        heads = {"s2_vm_auto": "stage 2 VM hat, auto route (V at the block's own options)",
                 "s2_vm_forced": "stage 2 VM hat under --engine=vm",
                 "s3_dfa": "stage 3 DFA hat (F, T = S ⊊ E)"}
        for k, rows in manif.items():
            with open(os.path.join(md, "manifest_%s.tsv" % k), "w") as f:
                f.write("# [START-SET] MOVER MANIFEST, %s. GENERATED by docs/design/startset/s1/census_s1.py\n" % heads[k])
                f.write("# at stage 1 (lane ssbuild01) from the built start_set fact; the stage that builds the hat\n")
                f.write("# checks its own movers against it (0 off-diagonal). Regenerating the census MOVES THIS CHECK.\n")
                f.write("#id\toptions\tpattern_hex\n")
                for b in sorted(rows, key=lambda b: (b["id"], b["args"])):
                    f.write("%s\t%s\t%s\n" % (b["id"], " ".join(b["args"]), b["pattern"].hex()))
    print(open(os.path.join(OUT, "census_s1_summary.txt")).read())


main()

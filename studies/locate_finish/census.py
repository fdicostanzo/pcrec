#!/usr/bin/env python3
"""LOCATE x FINISH census (lane locfin, D156): which locator and which finisher
every artifact gets TODAY, and the populations the new rows of
docs/design/locate_finish.md would reach.  COMPILE-SIDE ONLY: no subject is
matched, no clock is read.

Populations and the end-pin probe are BORROWED, not copied, from the
[OPT-REVEND] census (docs/dev/optloop/revend/census.py: bench_pop, corpus_pop,
run_probe; revend_probe.c built from its committed source against THIS
tree's libpcrec.a), so the two censuses count the same rows the same way.

Per row, two instruments that share no source:
  FACTS  `pcrec --emit-facts=<enc> --features all`: the `kinds` fact and the
         artifact's decision stamps (RX_ENGINE, RX_VM_PREFILTER[_LANG],
         RX_DFA_SCAN, RX_DFA_START, RX_DFA_MATCH, RX_END_WINDOW, ...), read
         off the emitted C by the compiler's own listing.
  TEXT   for every row the stamps call a VM hybrid or a DFA artifact: the
         emitted C itself, grepped for the reverse machine's accessor family
         (any `rx_reverse_` identifier: the uniform-fold representation has no
         `rx_reverse_next_state`, measured on 146 artifacts the first run's
         narrower marker misread) and for the inlined prefilter
         (`rx_prefilter(`).  The stamp says which pass a reader is TOLD runs;
         the text says which tables are THERE.  Disagreements are counted.

Env: PCREC (build/pcrec), PROBE (the built revend_probe), BENCH (pcrec-bench
checkout, read-only), CORPUS (this tree), OUT (output dir), JOBS (default 4),
REVEND_CENSUS (path to docs/dev/optloop/revend/census.py), TMP (scratch dir).

    PCREC=build/pcrec PROBE=.scratch/revend_probe BENCH=../pcrec-bench \
    CORPUS=. OUT=studies/locate_finish/results TMP=.scratch \
    REVEND_CENSUS=docs/dev/optloop/revend/census.py \
    python3 studies/locate_finish/census.py
"""
import concurrent.futures as cf
import importlib.util
import os
import re
import subprocess
import sys
import tempfile

E = os.environ
PCREC, OUT, TMP = E["PCREC"], E["OUT"], E["TMP"]
JOBS = int(E.get("JOBS", "4"))
TIMEOUT = ["gnutimeout", "120"]

spec = importlib.util.spec_from_file_location("revend_census", E["REVEND_CENSUS"])
rvc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rvc)          # reads PCREC/PROBE/BENCH/CORPUS/OUT itself

STAMPS = ["ENGINE", "ENGINE_SEL", "VM_PREFILTER", "VM_PREFILTER_LANG", "DFA_SCAN",
          "DFA_START", "DFA_MATCH", "DFA_PREFILTER", "END_WINDOW", "REQ_HANDOFF",
          "VM_START", "VM_START_SCAN", "VM_PRUNE_CEILING", "NCAPS"]


def base_cmd(r):
    cmd = [PCREC, "--features", "all"]
    if r["icase"]:
        cmd.append("-i")
    if r["enc"] == "utf8":
        cmd += ["-e", "utf8"]
    return cmd


def facts(r):
    cmd = TIMEOUT + base_cmd(r)[:1] + ["--emit-facts=" + r["enc"]] + base_cmd(r)[1:] + \
        ["--pattern", r["pat"]]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        return {"refused": "timeout"}
    if p.returncode != 0:
        return {"refused": p.stderr.decode("utf8", "replace").split("\n")[0][:100]}
    d, sect = {}, None
    for ln in p.stdout.decode("utf8", "replace").split("\n"):
        if ln.startswith("#section"):
            sect = ln.split()[1]
            continue
        if ln.startswith("#") or not ln:
            continue
        f = ln.split("\t")
        if sect == "facts" and len(f) >= 7 and f[1] in ("kinds", "start_anchor", "end_window"):
            d["f_" + f[1]] = f[6]
        elif sect == "decisions" and len(f) >= 3 and f[1].startswith("RX_"):
            k = f[1][3:]
            if k in STAMPS:
                d[k] = f[2].strip('"')
    return d


def text(r):
    """The emitted C itself: does it carry a reverse machine, an inlined
    prefilter, an anchored DFA match machine?"""
    with tempfile.TemporaryDirectory(dir=TMP) as td:
        out = os.path.join(td, "a.c")
        cmd = TIMEOUT + base_cmd(r) + ["-p", "rx", "-o", out, "--pattern", r["pat"]]
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=180)
        except subprocess.TimeoutExpired:
            return {"t_ok": "timeout"}
        if p.returncode != 0:
            return {"t_ok": "refused"}
        src = open(out, "rb").read()
    return {"t_ok": "ok",
            "t_rev": int(b"rx_reverse_" in src),
            "t_pref": int(b"rx_prefilter(" in src)}


def kinds(r):
    return set((r.get("f_kinds") or "").split(",")) - {""}


def classify(r):
    """TODAY's (locator, finisher) pair, read from the stamps (locate_finish.md
    §3.1's table).  The class names are the note's."""
    eng = r.get("ENGINE")
    if not eng:
        return "refused", "-"
    k = kinds(r)
    if eng == "dfa":
        scan, start = r.get("DFA_SCAN"), r.get("DFA_START")
        if scan == "empty":
            return "L-empty", "F-nomatch"
        if scan == "attempt":
            return "L-candloop", "F-anch-dfa"
        if start == "pinned":
            return "L-pinned", "F-none"
        return "L-fwdrev", "F-none"
    # VM
    if r.get("VM_PREFILTER") == "hybrid":
        exact = (r.get("VM_PREFILTER_LANG") == "exact" and "atomic" not in k
                 and "lookaround" not in k)
        scan, start = r.get("DFA_SCAN"), r.get("DFA_START")
        loc = {"empty": "P-empty", "attempt": "P-candloop"}.get(
            scan, "P-pinned" if start == "pinned" else "P-fwdrev")
        return loc, "F-vm-span" if exact else "F-vm-cand"
    return "L-trivial", "F-vm-search"


def pinned_view(r):
    return r.get("status") == "ok" and r.get("view") in (1, 2) and not r.get("gstart")


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = rvc.bench_pop() + rvc.corpus_pop()
    pr = rvc.run_probe(rows)
    for i, r in enumerate(rows):
        r.update(pr.get(i, dict(status="noprobe", view=0, cwmax=-1, minw=0,
                                lead_unb=0, gstart=0, look_tail=0)))
    with cf.ThreadPoolExecutor(max_workers=JOBS) as ex:
        for r, d in zip(rows, ex.map(facts, rows)):
            r.update(d)
    # TEXT on every compiled row: the control reads all of them, so a stamp
    # class cannot hide a population the text would show.
    comp = [r for r in rows if r.get("ENGINE")]
    with cf.ThreadPoolExecutor(max_workers=JOBS) as ex:
        for r, d in zip(comp, ex.map(text, comp)):
            r.update(d)
    for r in rows:
        r["loc"], r["fin"] = classify(r)
        r["endpin"] = int(pinned_view(r))
    keys = ["pop", "id", "suite", "enc", "icase", "status", "view", "cwmax", "minw",
            "lead_unb", "gstart", "f_kinds", "f_start_anchor", "f_end_window"] + STAMPS + \
        ["refused", "t_ok", "t_rev", "t_pref", "loc", "fin", "endpin", "pattern_hex"]
    with open(os.path.join(OUT, "rows.tsv"), "w") as fh:
        fh.write("\t".join(keys) + "\n")
        for r in rows:
            v = dict(r)
            v["pattern_hex"] = r["pat"].hex()
            fh.write("\t".join(str(v.get(k, "")) for k in keys) + "\n")
    print("rows", len(rows), "compiled", len(comp))


if __name__ == "__main__":
    sys.exit(main())

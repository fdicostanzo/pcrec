#!/usr/bin/env python3
"""[ART-POSS-ARMS] §8.6's K35 re-count, against the BUILT compiler and
independent of the prototype: the same two populations as rev21/r21_census.py
(ARTREV's loaders, pcrec-bench read-only + every distinct corpus .rxt
pattern), counted three ways that share no code with the prototype:

  1. the DENY-DELTA census: `--engine=vm --emit-ir`'s `possessify
     marked/total` with both arms denied, with each arm alone, and armed;
  2. the STAMP census: `RX_VM_POSS_ARMS` on the armed --engine=vm artifact
     and on the armed default-route artifact;
  3. the default-route ENGINE denied (both deny bits) vs armed (C-1's
     route-flip census).

`--diff FILE` then compares against the prototype's census_r21.tsv by
(pop, id, enc): vm_base vs denied, vm_AB vs armed, eng_base/eng_AB. Any
difference is printed; the caller explains it or it is a defect.

Env: PCREC (the built compiler), ARTREV_GEN (dir holding census.py),
BENCH, CORPUS, JOBS."""
import os, sys, re, subprocess, concurrent.futures as cf
sys.path.insert(0, os.environ["ARTREV_GEN"])
import census as C
B = os.environ["PCREC"]
DA, DB = "-fno-poss-ctx-follow", "-fno-poss-bref-first"

def run(cmd):
    try:
        p = subprocess.run([B] + cmd, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    if p.returncode:
        return None, p.stderr.decode("utf8", "replace").split("\n")[0][:120]
    return p.stdout.decode("latin-1"), None

def marked(ir):
    for ln in (ir or "").split("\n"):
        f = ln.split("\t")
        if f[0] == "possessify" and len(f) > 1: return f[1]
    return None

def stamp(c, name):
    m = re.search(r'#define RX_%s "?([\w]+)' % name, c or "")
    return m.group(1) if m else ""

def one(r):
    o = C.opts(r)
    vm = o + ["--engine=vm", "--emit-ir", "--pattern", r["pat"]]
    res = dict(pop=r["pop"], id=r["id"], enc=r["enc"])
    ir, err = run([DA, DB] + vm)
    res["vm_denied"] = marked(ir)
    res["refused"] = "" if ir else (err or "?").replace("\t", " ")
    if ir:
        res["vm_Aonly"] = marked(run([DB] + vm)[0])
        res["vm_Bonly"] = marked(run([DA] + vm)[0])
        res["vm_armed"] = marked(run(vm)[0])
        c, _ = run(["-p", "rx"] + o + ["--engine=vm", "-o", "-", "--pattern", r["pat"]])
        res["stamp_vm"] = stamp(c, "VM_POSS_ARMS")
    for k, ex in (("denied", [DA, DB]), ("armed", [])):
        c, err = run(["-p", "rx"] + ex + o + ["-o", "-", "--pattern", r["pat"]])
        res["eng_" + k] = stamp(c, "ENGINE") or ("refused" if c is None else "?")
        if k == "armed": res["stamp_def"] = stamp(c, "VM_POSS_ARMS")
    return res

KEYS = ["pop", "id", "enc", "vm_denied", "vm_Aonly", "vm_Bonly", "vm_armed",
        "stamp_vm", "stamp_def", "eng_denied", "eng_armed", "refused"]

def census():
    rows = C.bench_pop() + C.corpus_pop()
    with cf.ThreadPoolExecutor(int(os.environ.get("JOBS", "8"))) as ex:
        out = list(ex.map(one, rows))
    print("\t".join(KEYS))
    for r in out:
        print("\t".join(str(r.get(k, "") or "") for k in KEYS))

def load(f):
    lines = open(f).read().rstrip("\n").split("\n")
    h = lines[0].split("\t")
    return {(d["pop"], d["id"], d["enc"]): d
            for d in (dict(zip(h, l.split("\t"))) for l in lines[1:])}

def diff(mine, proto):
    a, p = load(mine), load(proto)
    nd = 0
    for k in sorted(set(a) | set(p)):
        x, y = a.get(k), p.get(k)
        if not x or not y:
            print("ONLY-IN-%s\t%s" % ("build" if x else "proto", "\t".join(k))); nd += 1; continue
        for mk, pk in (("vm_denied", "vm_base"), ("vm_armed", "vm_AB"),
                       ("eng_denied", "eng_base"), ("eng_armed", "eng_AB")):
            xv, yv = x.get(mk) or "", y.get(pk) or ""
            if yv == "None": yv = ""
            if xv != yv:
                print("DIFF\t%s\t%s=%s\t%s=%s" % ("\t".join(k), mk, xv, pk, yv)); nd += 1
    print("diff-rows\t%d" % nd)

if len(sys.argv) > 2 and sys.argv[1] == "--diff":
    diff(sys.argv[2], sys.argv[3])
else:
    census()

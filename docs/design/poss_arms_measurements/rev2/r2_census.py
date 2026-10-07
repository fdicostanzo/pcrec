#!/usr/bin/env python3
"""[ART-POSS-ARMS] rev 2 census (K35 + C-1's ROUTE-FLIP census).

Drives the rev-2 SCRATCH PROTOTYPE (proto_rev2.patch, env-switched) over
[ARTREV]'s populations (census.py's loaders: every pcrec-bench
bench/*/patterns/*.rx, read-only, and every distinct corpus .rxt pattern).

Per pattern it records:
  - `possessify marked/total` from `--engine=vm --emit-ir` under each arm
    configuration in VM_ARMS (base = no arm, i.e. today's main);
  - the DEFAULT-route engine (RX_ENGINE) and RX_ENGINE_WHY under BOTH the
    denied build and the armed build (the rev-1 census recorded only the
    last one it saw -- C-1);
  - the default artifact's RX_PUSH( site count and RX_VM_FRAMELESS;
  - for a pattern the base `--engine=vm` compile REFUSES, the first line of
    its diagnostic (the census denominator and refused list, B-M4).

Env: PROTO (prototype binary), PCREC (main build, for --list-source),
ARTREV_GEN (dir holding census.py), BENCH, CORPUS, JOBS, LIMIT."""
import os, sys, re, subprocess, concurrent.futures as cf
sys.path.insert(0, os.environ["ARTREV_GEN"])
import census as C
PROTO = os.environ["PROTO"]
VM_ARMS = {
    "base": {}, "A": {"PROTO_ARM_A": "1"}, "B": {"PROTO_ARM_B": "1"},
    "AB": {"PROTO_ARM_A": "1", "PROTO_ARM_B": "1"},
    "A0": {"PROTO_ARM_A": "1", "PROTO_A0_ONLY": "1"},
    "A1": {"PROTO_ARM_A": "1", "PROTO_A1_ONLY": "1"},
    "ABnocc": {"PROTO_ARM_A": "1", "PROTO_ARM_B": "1", "PROTO_A1_NOCC": "1"},
    "ABa0null": {"PROTO_ARM_A": "1", "PROTO_ARM_B": "1", "PROTO_A0_NULLABLE": "1"},
}
DEF_ARMS = {"base": {}, "AB": VM_ARMS["AB"]}

def run(cmd, env_extra):
    env = dict(os.environ); env.update(env_extra)
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=120, env=env)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    if p.returncode:
        return None, p.stderr.decode("utf8", "replace").split("\n")[0][:120]
    return p.stdout.decode("latin-1"), None

def one(r):
    o = C.opts(r)
    res = dict(pop=r["pop"], id=r["id"], enc=r["enc"])
    for k, ev in VM_ARMS.items():
        ir, err = run([PROTO] + o + ["--engine=vm", "--emit-ir", "--pattern", r["pat"]], ev)
        m = None
        if ir:
            for ln in ir.split("\n"):
                f = ln.split("\t")
                if f[0] == "possessify" and len(f) > 1:
                    m = f[1]; break
        res["vm_" + k] = m
        if k == "base":
            res["refused"] = "" if ir else (err or "?").replace("\t", " ")
    for k, ev in DEF_ARMS.items():
        c, err = run([PROTO, "-p", "rx"] + o + ["-o", "-", "--pattern", r["pat"]], ev)
        if c is None:
            res["eng_" + k] = None; res["why_" + k] = (err or "?").replace("\t", " ")
            res["def_" + k] = None
            continue
        eng = re.search(r'#define RX_ENGINE "?(\w+)', c)
        why = re.search(r'#define RX_ENGINE_WHY "(.*)"', c)
        res["eng_" + k] = eng.group(1) if eng else "?"
        res["why_" + k] = why.group(1) if why else ""
        res["def_" + k] = "%d/%s" % (c.count("RX_PUSH("),
                                     "frameless" if re.search(r"RX_VM_FRAMELESS 1", c) else "framed")
    return res

def main():
    rows = C.bench_pop() + C.corpus_pop()
    lim = int(os.environ.get("LIMIT", "0"))
    if lim: rows = rows[:lim]
    with cf.ThreadPoolExecutor(int(os.environ.get("JOBS", "4"))) as ex:
        out = list(ex.map(one, rows))
    keys = (["pop", "id", "enc"] + ["vm_" + k for k in VM_ARMS] +
            ["eng_base", "eng_AB", "def_base", "def_AB", "why_base", "why_AB", "refused"])
    print("\t".join(keys))
    for r in out:
        print("\t".join(str(r.get(k)) for k in keys))
main()

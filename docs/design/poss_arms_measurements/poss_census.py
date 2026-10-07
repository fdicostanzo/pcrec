#!/usr/bin/env python3
"""[ART-POSS-ARMS] K35 census: which bench/corpus patterns each arm FIRES on,
measured with a SCRATCH PROTOTYPE of the two arms (env-switched), against the
same compiler with neither arm.  Populations are [ARTREV] census.py's own
(bench/*/patterns/*.rx and every .rxt pattern via --list-source)."""
import os, sys, re, subprocess, concurrent.futures as cf
sys.path.insert(0, os.environ["ARTREV_GEN"])
import census as C
PROTO = os.environ["PROTO"]
def run(cmd, env_extra):
    env = dict(os.environ); env.update(env_extra)
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=120, env=env)
    except subprocess.TimeoutExpired:
        return None
    if p.returncode: return None
    return p.stdout.decode("latin-1")
ARMS = {"base": {}, "A": {"PROTO_ARM_A": "1"}, "B": {"PROTO_ARM_B": "1"},
        "AB": {"PROTO_ARM_A": "1", "PROTO_ARM_B": "1"}}
def one(r):
    o = C.opts(r)
    res = dict(pop=r["pop"], id=r["id"], enc=r["enc"])
    for k, ev in ARMS.items():
        ir = run([PROTO] + o + ["--engine=vm", "--emit-ir", "--pattern", r["pat"]], ev)
        m = None
        if ir:
            for ln in ir.split("\n"):
                f = ln.split("\t")
                if f[0] == "possessify" and len(f) > 1:
                    m = f[1]; break
        res["vm_" + k] = m
    for k in ("base", "AB"):
        c = run([PROTO, "-p", "rx"] + o + ["-o", "-", "--pattern", r["pat"]], ARMS[k])
        if c is None:
            res["def_" + k] = None; continue
        eng = re.search(r"#define RX_ENGINE \"?(\w+)", c)
        res["eng"] = eng.group(1) if eng else "?"
        res["def_" + k] = "%d/%s" % (c.count("RX_PUSH("), "frameless" if re.search(r"RX_VM_FRAMELESS 1", c) else "framed")
    return res
def main():
    rows = C.bench_pop() + C.corpus_pop()
    lim = int(os.environ.get("LIMIT", "0"))
    if lim: rows = rows[:lim]
    with cf.ThreadPoolExecutor(4) as ex:
        out = list(ex.map(one, rows))
    keys = ["pop", "id", "enc", "eng", "vm_base", "vm_A", "vm_B", "vm_AB", "def_base", "def_AB"]
    print("\t".join(keys))
    for r in out:
        print("\t".join(str(r.get(k)) for k in keys))
main()

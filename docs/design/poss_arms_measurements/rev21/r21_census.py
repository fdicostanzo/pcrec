#!/usr/bin/env python3
"""[ART-POSS-ARMS] rev 2.1 census: rev 2's (r2_census.py) re-run on the
rev-2.1 prototype, plus the two checks rev 2.1 adds, over the same
populations ([ARTREV]'s census.py loaders: pcrec-bench read-only, and every
distinct corpus .rxt pattern).

Per pattern:
  - `possessify marked/total` (--engine=vm --emit-ir) under base (no arm),
    AB on the rev-2.1 prototype (PROTO), and AB on the rev-2 prototype
    (PROTO2) -- the rev 2 -> rev 2.1 delta is N1's fix plus the memoized
    deeper reference resolution (R-4);
  - R-5: the same AB compile with PROTO_CHECK_FOLLOW=1. At every verdict the
    prototype compares A1's continuation fold, gates valued A0, with the
    walk's FOLLOW (bytes u ENCL, and end-reachability vs may_end), and the
    Q-independent summary (R-4's A1 half) with the fold. Recorded: counts of
    each outcome, and any R4SUM-MISMATCH;
  - the DEFAULT-route engine under base and AB (C-1's route-flip census).

Env: PROTO, PROTO2, PCREC (for --list-source), ARTREV_GEN, BENCH, CORPUS,
JOBS, LIMIT."""
import os, sys, re, subprocess, concurrent.futures as cf
sys.path.insert(0, os.environ["ARTREV_GEN"])
import census as C
PROTO, PROTO2 = os.environ["PROTO"], os.environ["PROTO2"]
AB = {"PROTO_ARM_A": "1", "PROTO_ARM_B": "1"}

def run(b, cmd, env_extra):
    env = dict(os.environ); env.update(env_extra)
    try:
        p = subprocess.run([b] + cmd, capture_output=True, timeout=300, env=env)
    except subprocess.TimeoutExpired:
        return None, "timeout", ""
    err = p.stderr.decode("utf8", "replace")
    if p.returncode:
        return None, err.split("\n")[0][:120], err
    return p.stdout.decode("latin-1"), None, err

def marked(ir):
    for ln in (ir or "").split("\n"):
        f = ln.split("\t")
        if f[0] == "possessify" and len(f) > 1: return f[1]
    return None

def one(r):
    o = C.opts(r)
    vm = o + ["--engine=vm", "--emit-ir", "--pattern", r["pat"]]
    res = dict(pop=r["pop"], id=r["id"], enc=r["enc"])
    ir, err, _ = run(PROTO, vm, {})
    res["vm_base"] = marked(ir)
    res["refused"] = "" if ir else (err or "?").replace("\t", " ")
    if ir:
        res["vm_AB"] = marked(run(PROTO, vm, AB)[0])
        res["vm_ABr2"] = marked(run(PROTO2, vm, AB)[0])
        e = dict(AB); e["PROTO_CHECK_FOLLOW"] = "1"
        _o, _e, stderr = run(PROTO, vm, e)
        cnt = {}
        for ln in stderr.split("\n"):
            if ln.startswith("R5\t"):
                k = ln[3:].replace("\t", "/"); cnt[k] = cnt.get(k, 0) + 1
            elif ln.startswith("R4SUM-MISMATCH"):
                cnt["R4SUM-MISMATCH"] = cnt.get("R4SUM-MISMATCH", 0) + 1
        res["r5"] = ",".join("%s=%d" % kv for kv in sorted(cnt.items()))
    for k, ev in (("base", {}), ("AB", AB)):
        c, err, _ = run(PROTO, ["-p", "rx"] + o + ["-o", "-", "--pattern", r["pat"]], ev)
        eng = re.search(r'#define RX_ENGINE "?(\w+)', c) if c else None
        res["eng_" + k] = eng.group(1) if eng else ("refused" if c is None else "?")
    return res

def main():
    rows = C.bench_pop() + C.corpus_pop()
    lim = int(os.environ.get("LIMIT", "0"))
    if lim: rows = rows[:lim]
    with cf.ThreadPoolExecutor(int(os.environ.get("JOBS", "4"))) as ex:
        out = list(ex.map(one, rows))
    keys = ["pop", "id", "enc", "vm_base", "vm_AB", "vm_ABr2", "eng_base", "eng_AB", "r5", "refused"]
    print("\t".join(keys))
    for r in out:
        print("\t".join(str(r.get(k, "")) for k in keys))
main()

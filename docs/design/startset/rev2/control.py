#!/usr/bin/env python3
"""[START-SET] rev 2: THE FACT'S CONTROL ON EVERY MACHINE, SEEDED INCLUDED,
WITH A FAILING DIRECTION IN THE WALK (review r4 checks-F2 (a), sound-F2).

For every census row whose auto artifact has a forward DFA (dfa route, or a
hybrid's inlined prefilter), read X off the emitted artifact: on a SEEDED
machine X = Tdfa (estar.py: the bytes that begin a live thread from SOME seed
state, plus s0); on an UNSEEDED one X = the emitted can_begin_match (today's
C-SS subject, summarize.py's E).  The expectation comes from the subset
construction, never from the walk.  Then, for the shipped walk and for each
planted walk defect (fs_probe_plant.c), check

    Tdfa <= S      wherever S is a necessary condition (non-nullable, |S| < 256)

Baseline must read 0 violations; each plant must read > 0, and its REACH (rows
whose S the plant changes) is reported beside its detections.

    control.py CENSUS_TSV OUT_TSV         Env: PCREC, FSPLANT (built probe), W, JOBS
"""
import csv, json, os, subprocess, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estar

PCREC = os.environ["PCREC"]; FSP = os.environ["FSPLANT"]; W = os.environ["W"]; JOBS = int(os.environ.get("JOBS", "6"))
PLANTS = ["", "cat-null", "alt-right", "look-eats", "rep-min0"]

def bits(h):
    b = bytes.fromhex(h); return {i for i in range(256) if b[i >> 3] >> (i & 7) & 1}

def tdfa(job):
    i, r = job
    o = os.path.join(W, "c%d.c" % i)
    extra = ["-e", "utf8"] if r["set"] == "utf8" else []
    c = subprocess.run([PCREC, "--features", "all", *extra, "-p", "rx", "-o", o, "--pattern", bytes.fromhex(r["pat_hex"])], capture_output=True)
    if c.returncode: return None
    st = estar.sets(o, "rx", "00" * 32)
    for f in (o, o[:-2] + ".h"):
        try: os.remove(f)
        except OSError: pass
    if st["status"] == "no-init": return ("unread", r["name"] + "(init)")
    if st["status"] != "ok": return None
    if st["nseeds"] > 1:                 # seeded: the machine's own floor, read only where the table is s0's escape set
        return (st["nseeds"], set(st["Tdfa"])) if st["cbm_agrees"] else ("unread", r["name"])
    # unseeded: today's C-SS reads the EMITTED table (a scan-edge start state
    # moves the first byte out of the transition table, so the machine read is
    # not the escape set there)
    return (1, set(st["Ecbm"])) if st["Ecbm"] is not None else ("unread", r["name"])

def probe(plant, rows):
    out = {}
    for enc in ("byte", "utf8"):
        sub = [(i, r) for i, r in rows if (r["set"] == "utf8") == (enc == "utf8")]
        inp = "".join("%d\t%s\n" % (i, r["pat_hex"]) for i, r in sub)
        env = dict(os.environ, PLANT=plant)
        res = subprocess.run([FSP] + (["-e", "utf8"] if enc == "utf8" else []), input=inp, capture_output=True, text=True, env=env, check=True)
        for l in res.stdout.splitlines()[1:]:
            f = l.split("\t")
            if f[1] == "ok": out[int(f[0])] = (f[2] == "1", bits(f[4]))
    return out

def main():
    rows = [r for r in csv.DictReader((l for l in open(sys.argv[1]) if not l.startswith("# ")), delimiter="\t")]
    pop = [(i, r) for i, r in enumerate(rows) if r["status"] == "ok" and r["a_RX_ENGINE"] in ("dfa", "vm")]
    with cf.ThreadPoolExecutor(JOBS) as ex: T = dict(zip([i for i, _ in pop], ex.map(tdfa, pop)))
    unread = [T[i][1] for i, _ in pop if T[i] is not None and T[i][0] == "unread"]
    pop = [(i, r) for i, r in pop if T[i] is not None and T[i][0] != "unread"]
    S = {p: probe(p, pop) for p in PLANTS}
    lines = []
    for p in PLANTS:
        n = viol = vs = reach = det = 0
        for i, r in pop:
            if i not in S[p]: continue
            nul, s = S[p][i]
            if nul or len(s) >= 256: continue
            n += 1; seeded = T[i][0] > 1
            v = not T[i][1] <= s
            viol += v; vs += v and seeded
            if p and S[""].get(i) != S[p][i]:
                reach += 1; det += v
        lines.append("plant=%s rows_checked=%d violations=%d (seeded %d, unseeded %d) reach=%d detected_in_reach=%d" % (p or "none", n, viol, vs, viol - vs, reach, det))
    with open(sys.argv[2], "w") as f:
        f.write("\n".join(lines) + "\n")
        f.write("population: %d dfa/hybrid artifacts read; seeded %d; unread %d (no emitted table, or a seeded table that is not s0's escape set): %s\n" % (
            len(pop), sum(T[i][0] > 1 for i, _ in pop), len(unread), ", ".join(unread[:12]) + (" ..." if len(unread) > 12 else "")))
    print(open(sys.argv[2]).read())

main()

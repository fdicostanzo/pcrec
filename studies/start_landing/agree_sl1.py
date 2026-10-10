#!/usr/bin/env python3
"""SL1's census agreement (see agree_sl1.sh). One row per compile where both
sides speak (the probe prints on a forward DFA form; the facts are derived on
the unanchored route): pid config enc probe_land built_land probe_w built_w
verdict. Verdicts: agree, disagree, capped (the probe's LP_MAXW = 4096 width
cap read a built bound above it as "not fixed": an instrument cap, counted).
"""
import os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

PC = sys.argv[1]
TMP = tempfile.mkdtemp(prefix="agree.", dir=os.environ.get("TMPDIR", "."))
MAP = {"OK": "one-char", "nullable": "decline:nullable",
       "assert-at-start": "decline:assert-at-start", "empty": "decline:dead-start",
       "alive-not-accept": "decline:alive-not-accept",
       "assert-after": "decline:assert-after"}


def esc(b):
    o = []
    for c in b:
        if c == 0x5c: o.append("\\\\")
        elif c == 0x22: o.append('\\"')
        elif 0x20 <= c < 0x7f: o.append(chr(c))
        else: o.append("\\x%02x" % c)
    return "".join(o)


def one(job):
    pid, enc, icase, pat, cfg = job
    base = [PC, "--features", "all"]
    if enc == "utf8": base += ["-e", "utf8"]
    if icase == "1": base.append("-i")
    if cfg == "nocaps": base.append("--no-captures")
    pe = ["--pattern-esc", "--pattern", "\"" + esc(pat) + "\""]
    out = os.path.join(TMP, "a%d.c" % os.getpid())
    try:
        r = subprocess.run(base + ["-p", "rx", "-o", out] + pe, capture_output=True,
                           timeout=300, env=dict(os.environ, PCREC_LANDPROBE="1"))
        q = subprocess.run(base + ["--emit-facts"] + pe, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode or q.returncode:
        return None
    lines = [l for l in r.stderr.decode("utf8", "replace").split("\n") if l.startswith("LANDPROBE")]
    facts = {}
    for l in q.stdout.decode("utf8", "replace").split("\n"):
        p = l.split("\t")
        if len(p) >= 8 and p[1] in ("land_char", "width"):
            facts[p[1]] = (p[4], p[6], p[7])
    if not lines or "land_char" not in facts or facts["land_char"][0] == "absent":
        return None
    f = dict(kv.split("=", 1) for kv in lines[-1].split("\t")[1:])
    st, val, why = facts["land_char"]
    built_land = (val.split("+")[0] if st == "derived" else why)
    probe_land = MAP.get(f["land"], "?" + f["land"])
    bw = facts["width"][1]
    pb, px = int(f["bmin"]), int(f["bmax"])
    probe_w = "none" if pb < 0 else ("[%d,inf)" % pb if px < 0 else "[%d,%d]" % (pb, px))
    verdict = "agree"
    if built_land != probe_land:
        verdict = "disagree"
    if built_land == "one-char" and ("+guard" in val) != (f["hi"] == "1"):
        verdict = "disagree"
    if bw != probe_w:
        hi = bw.strip("[]").split(",")
        if (verdict == "agree" and px < 0 and len(hi) == 2 and hi[1].isdigit()
                and int(hi[1]) > 4096 and probe_w == "[%d,inf)" % pb):
            verdict = "capped"
        else:
            verdict = "disagree"
    return [pid, cfg, enc, probe_land, built_land + ("+guard" if "+guard" in val else ""),
            probe_w, bw, verdict]


jobs, seen = [], set()
for pop in sys.argv[2:]:
    for line in open(pop):
        f = line.rstrip("\n").split("\t")
        if f[0] == "pid": continue
        key = (f[0], f[2], f[3], f[4])
        if key in seen: continue
        seen.add(key)
        for cfg in ("default", "nocaps"):
            jobs.append((f[0], f[2], f[3], bytes.fromhex(f[4]), cfg))
tally = {}
print("pid\tconfig\tenc\tprobe_land\tbuilt_land\tprobe_w\tbuilt_w\tverdict")
with ThreadPoolExecutor(int(os.environ.get("JOBS", "8"))) as ex:
    for row in ex.map(one, jobs):
        if row is None:
            tally["no-e3"] = tally.get("no-e3", 0) + 1
            continue
        tally[row[-1]] = tally.get(row[-1], 0) + 1
        print("\t".join(row), flush=True)
print("AGREE_SL1 compiles=%d %s" % (len(jobs), " ".join("%s=%d" % kv for kv in sorted(tally.items()))),
      file=sys.stderr)

#!/usr/bin/env python3
"""[START-LANDING] the FACT CENSUS (STUDY; never built or run by make).

    census.py PROTO_PCREC POP.tsv [JOBS] > out.tsv

PROTO_PCREC is pcrec built WITH proto.patch applied (a scratch build: the
patch only PRINTS, under PCREC_LANDPROBE, the facts the design's RECOVER rows
read; it selects nothing and moves no artifact). POP.tsv is walk_survey's
population file (pop_bench.py / pop_corpus.py: pid set enc icase pattern_hex
...). One compile per distinct (pid, enc, icase, pattern) x config
(default, nocaps), with the bench's own flags (`--features all`, `-e utf8`,
`-i`, `--no-captures`). Output, one row per compile:

  pid config enc rc route fit next seeded land fixedw recover mb row

`row` is the design's first-match RECOVER selection, computed HERE from the
printed facts by the design's predicates (§3 of docs/design/start_landing.md):
  pinned          today's `pinned` already selected (unchanged)
  end-minus-width route dfa, fixedw >= 0
  landing         route dfa, land OK, not seeded, next != none
  reverse-pass    otherwise (route dfa)
  -               route attempt / no DFA body (RECOVER not asked)
"""
import os, subprocess, sys, tempfile, threading
from concurrent.futures import ThreadPoolExecutor

PC, POP = sys.argv[1], sys.argv[2]
JOBS = int(sys.argv[3]) if len(sys.argv) > 3 else 2
TMP = tempfile.mkdtemp(prefix="landcen.", dir=os.environ.get("TMPDIR", "."))


def esc(b):
    o = []
    for c in b:
        if c == 0x5c: o.append("\\\\")
        elif c == 0x22: o.append('\\"')
        elif 0x20 <= c < 0x7f: o.append(chr(c))
        else: o.append("\\x%02x" % c)
    return "".join(o)


def row_of(f):
    if f.get("route") != "dfa":
        return "-"
    if f["recover"] == "pinned":
        return "pinned"
    if int(f["fixedw"]) >= 0:
        return "end-minus-width"
    if f["land"] == "OK" and f["seeded"] == "0" and f["next"] != "none":
        return "landing"
    return "reverse-pass"


def one(job):
    pid, enc, icase, pat, cfg = job
    out = os.path.join(TMP, "a%d.c" % threading.get_ident())
    args = [PC, "--features", "all", "-p", "rx", "-o", out]
    if enc == "utf8": args += ["-e", "utf8"]
    if icase == "1": args.append("-i")
    if cfg == "nocaps": args.append("--no-captures")
    args += ["--pattern-esc", "--pattern", "\"" + esc(pat) + "\""]
    env = dict(os.environ, PCREC_LANDPROBE="1")
    try:
        r = subprocess.run(args, capture_output=True, timeout=300, env=env)
    except subprocess.TimeoutExpired:
        return [pid, cfg, enc, "TIMEOUT"] + ["-"] * 9
    lines = [l for l in r.stderr.decode("utf8", "replace").split("\n") if l.startswith("LANDPROBE")]
    if r.returncode != 0:
        return [pid, cfg, enc, "REFUSED"] + ["-"] * 9
    if not lines:   # no forward DFA form derived: VM-only or ENG_ATTEMPT-only
        return [pid, cfg, enc, "ok", "none"] + ["-"] * 8
    f = dict(kv.split("=", 1) for kv in lines[-1].split("\t")[1:])
    return [pid, cfg, enc, "ok", f["route"], f["fit"], f["next"], f["seeded"], f["land"],
            f["fixedw"], f["recover"], f["mb"], row_of(f)]


jobs, seen = [], set()
for line in open(POP):
    f = line.rstrip("\n").split("\t")
    if f[0] == "pid": continue
    key = (f[0], f[2], f[3], f[4])
    if key in seen: continue
    seen.add(key)
    for cfg in ("default", "nocaps"):
        jobs.append((f[0], f[2], f[3], bytes.fromhex(f[4]), cfg))

print("\t".join("pid config enc rc route fit next seeded land fixedw recover mb row".split()))
with ThreadPoolExecutor(JOBS) as ex:
    for out in ex.map(one, jobs):
        print("\t".join(out), flush=True)

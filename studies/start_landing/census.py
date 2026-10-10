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
      bmin bmax hi ldepth

[rev 2, lane landrev] The probe (proto.patch rev 2) also prints the byte width
INTERVAL [bmin, bmax] from one union-frontier iterator (SL-G3; `fixedw` is
kept as the cross-check: W >= 0 must equal bmin == bmax), `hi` (a first byte
above the seam's `onebyte_max`: the rows where the guard is emitted, SL-G2),
`ldepth` (the deepest mid-character frontier Λ's walk reached), and a
LANDEMPTY line on an EMPTY engine (SL-C1). An empty artifact (`RX_DFA_SCAN
"empty"`) is row `empty`: RECOVER is off its path, every new row declines
there (the shared `recover_on_path` conjunct, design §4.1), and its W is
reported so the population the conjunct protects is counted, not assumed.

`row` is the design's first-match RECOVER selection, computed HERE from the
printed facts by the design's predicates (§3 of docs/design/start_landing.md):
  pinned          today's `pinned` already selected (unchanged)
  end-minus-width route dfa, fixedw >= 0
  landing         route dfa, land OK, not seeded, next != none
  reverse-pass    otherwise (route dfa)
  empty           the empty engine (rev 2): no row may take it
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
        return [pid, cfg, enc, "TIMEOUT"] + ["-"] * 13
    err = r.stderr.decode("utf8", "replace").split("\n")
    lines = [l for l in err if l.startswith("LANDPROBE")]
    empt = [l for l in err if l.startswith("LANDEMPTY")]
    if r.returncode != 0:
        return [pid, cfg, enc, "REFUSED"] + ["-"] * 13
    if empt:
        try:
            art = open(out, encoding="latin-1").read()
        except OSError:
            art = ""
        if 'DFA_SCAN "empty"' in art:
            f = dict(kv.split("=", 1) for kv in empt[-1].split("\t")[1:])
            return [pid, cfg, enc, "ok", "dfa", "-", "-", "-", "-", f["fixedw"], f["recover"], "-",
                    "empty", f["bmin"], f["bmax"], "-", "-"]
    if not lines:   # no forward DFA form derived: VM-only or ENG_ATTEMPT-only
        return [pid, cfg, enc, "ok", "none"] + ["-"] * 12
    f = dict(kv.split("=", 1) for kv in lines[-1].split("\t")[1:])
    # the LAST probe line may come from an ABANDONED fit-ladder attempt (a
    # size-cap drop of the prefilter, say): the emitted artifact is the
    # judge of whether a DFA body, hence RECOVER, survived
    try:
        art = open(out, encoding="latin-1").read()
    except OSError:
        art = ""
    if '_DFA_START "' not in art:
        return [pid, cfg, enc, "ok", "none"] + ["-"] * 12
    return [pid, cfg, enc, "ok", f["route"], f["fit"], f["next"], f["seeded"], f["land"],
            f["fixedw"], f["recover"], f["mb"], row_of(f), f["bmin"], f["bmax"], f["hi"], f["ldepth"]]


jobs, seen = [], set()
for line in open(POP):
    f = line.rstrip("\n").split("\t")
    if f[0] == "pid": continue
    key = (f[0], f[2], f[3], f[4])
    if key in seen: continue
    seen.add(key)
    for cfg in ("default", "nocaps"):
        jobs.append((f[0], f[2], f[3], bytes.fromhex(f[4]), cfg))

print("\t".join("pid config enc rc route fit next seeded land fixedw recover mb row bmin bmax hi ldepth".split()))
with ThreadPoolExecutor(JOBS) as ex:
    for out in ex.map(one, jobs):
        print("\t".join(out), flush=True)

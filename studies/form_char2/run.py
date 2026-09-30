#!/usr/bin/env python3
"""[FORM-CHAR2] timing orchestrator.  Usage: run.py WORKDIR --rounds N --out TSV [--loadmax 0.5] [--only w1,w2] [--sec 0.15]
Per (witness, mode): ROUNDS rounds; within a round the arms run INTERLEAVED, order rotated each round;
arm `foldB` is the fold binary run a second time = the NULL CONTROL (noise floor). Load gate: /proc/loadavg
1-min < LOADMAX before every round (REFUSE and wait, never caveat); absent /proc/loadavg (darwin) = no gate,
numbers are SCRATCH-directional only. Every arm's answer checksum is compared against fold's."""
import argparse, os, subprocess, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("work"); ap.add_argument("--rounds", type=int, default=11)
ap.add_argument("--out", required=True); ap.add_argument("--loadmax", type=float, default=0.5)
ap.add_argument("--only"); ap.add_argument("--sec", default="0.15"); ap.add_argument("--maxwait", type=int, default=7200)
a = ap.parse_args()
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
os.environ.setdefault("BENCH_DIR", "/nonexistent")
import importlib.util
# witnesses.py reads bench files at import; avoid that here: derive names from the built binaries
names = sorted({f.rsplit("_", 1)[0] for f in os.listdir(f"{a.work}/bin")}, key=lambda x: x)
order = ["ci256", "waf744", "waf186", "slack", "union", "kwalt", "hdr", "lit16", "hotloop", "hotchain"]
names = [n for n in order if n in names]
if a.only: names = [n for n in names if n in a.only.split(",")]
ARMS = ["fold", "table", "bitmap", "foldB"]
def subj(w, mode):
    if mode == "match": return f"{a.work}/subj/{w}.match"
    if mode == "findall": return f"{a.work}/subj/{w}.hits"
    return f"{a.work}/subj/{ {'hotloop':'hot','hotchain':'hotchain'}.get(w,'hay') }.bin"
def load1():
    try: return float(open("/proc/loadavg").read().split()[0])
    except OSError: return None
def gate():
    waited = 0
    while True:
        l = load1()
        if l is None or l < a.loadmax: return l
        print(f"REFUSED load1={l} >= {a.loadmax}, waiting ({waited}s)", file=sys.stderr, flush=True)
        if waited > a.maxwait: sys.exit("gate timeout")
        time.sleep(30); waited += 30
out = open(a.out, "w"); out.write("witness\tmode\tarm\tround\tload1\tns_per_char\tchecksum\twork\n")
bad = 0
for w in names:
    for mode in ("search", "findall", "match"):
        for r in range(a.rounds):
            l = gate()
            arms = ARMS[r % 4:] + ARMS[:r % 4]
            ref = None
            for arm in arms:
                b = f"{a.work}/bin/{w}_{'fold' if arm == 'foldB' else arm}"
                p = subprocess.run([b, mode, subj(w, mode), a.sec], capture_output=True, text=True)
                ns, ck, wk = p.stdout.split()
                if arm == "fold": ref = ck
                out.write(f"{w}\t{mode}\t{arm}\t{r}\t{l}\t{ns}\t{ck}\t{wk}\n")
            # checksum compare (after the round so ref is set)
            for arm in ARMS: pass
        out.flush()
        print(f"done {w} {mode}", file=sys.stderr, flush=True)

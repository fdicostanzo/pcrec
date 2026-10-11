#!/usr/bin/env python3
"""lossreview/misc: per-phase subject-load counts for ONE bench pattern under
named pcrec flag VARIANTS (e.g. today vs -fno-rev-end), via walk_survey's
wsbuild.py + the mc-counting driver.  Counts only; nothing is timed.

    wsvar.py POP.tsv PID REGIME OUTROOT 'name1=--flag a --flag b' 'name2=' ...

POP.tsv rows come from studies/walk_survey/pop_bench.py. Env as run_pop.py
(PCREC, WSHERE=studies/walk_survey dir, WSDRV=wsdrv_mc.c). Prints, per
variant and config (default/nocaps): subjects, n, rx_search calls, matches,
memchr calls (mc), memcmp calls, total loads T, bytes through scanners and
loads per phase.  The pattern is passed --pattern-esc, byte-exact.
"""
import os, subprocess, sys, shlex, collections
sys.path.insert(0, os.environ["WSHERE"])
from importlib import import_module
pop, pid, regime, outroot = sys.argv[1:5]
variants = [v.split("=", 1) for v in sys.argv[5:]]
PCREC = os.environ["PCREC"]; HERE = os.environ["WSHERE"]
def esc(b):
    o = []
    for c in b:
        if c == 0x5c: o.append("\\\\")
        elif c == 0x22: o.append('\\"')
        elif 0x20 <= c < 0x7f: o.append(chr(c))
        else: o.append("\\x%02x" % c)
    return "".join(o)
row = [l.split("\t") for l in open(pop).read().split("\n")[1:] if l.startswith(pid + "\t") and l.split("\t")[5] == regime][0]
enc, pat, subs = row[2], bytes.fromhex(row[4]), row[6].split(",")
mode = {"match": "match", "search_short": "search", "throughput": "findall"}[regime]
PH = "pre skip fwd rev anc vm endw misc unk".split()
print("variant\tconfig\tsubjects\tn\tcalls\tnmatch\tmc\tmcmp\tT\tT_scan\t" + "\t".join("T_" + p for p in PH))
for name, flags in variants:
    for cfg in ("default", "nocaps"):
        art = os.path.join(outroot, "%s_%s_%s" % (pid.replace("/", "_"), name, cfg)); os.makedirs(art, exist_ok=True)
        args = ["--features", "all"] + (["-e", "utf8"] if enc == "utf8" else []) + (["--no-captures"] if cfg == "nocaps" else []) + shlex.split(flags)
        args += ["--pattern-esc", "--pattern", '"' + esc(pat) + '"']
        b = subprocess.run([sys.executable, os.path.join(HERE, "wsbuild.py"), PCREC, art] + args, capture_output=True)
        if b.returncode: print(name, cfg, "BUILD", b.returncode, b.stdout.decode()[:200]); continue
        p = subprocess.run(["/usr/bin/gnutimeout", "-s", "KILL", "600", os.path.join(art, "bin"), os.path.join(art, "map"), mode, "1" if enc == "utf8" else "0"] + subs, capture_output=True)
        L = p.stdout.decode().rstrip("\n").split("\n"); h = L[0].split("\t")
        a = collections.Counter()
        for l in L[1:]:
            d = dict(zip(h, l.split("\t")))
            a["subjects"] += 1
            for c in ["n", "calls", "nmatch", "mc", "mcmp", "T", "T_scan"] + ["T_" + x for x in PH]: a[c] += int(d.get(c) or 0)
        print("\t".join([name, cfg] + [str(a[c]) for c in ["subjects", "n", "calls", "nmatch", "mc", "mcmp", "T", "T_scan"] + ["T_" + x for x in PH]]))

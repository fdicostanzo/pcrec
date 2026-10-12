#!/usr/bin/env python3
"""[MATCH-SPLIT] STEP-0 (d): counted work for the quadratic-risk population (a WORK count: subject-byte
loads of a whole find-all, and attempt-loop entries where the artifact has one; no clock).

For each pattern whose END path is led by an unbounded repeat and whose route tries every start
(dfa/hybrid attempt, or VM-only), plus a linear CONTROL set (rev-end routes), build the artifact
instrumented as qdrv.c describes and run a find-all over  Q . c*k . Q  (an INTERNAL run, k in
{1000, 4000, 16000}), over  Q . c*k  (a TRAILING run) and over  c*k  (the whole-subject run).  The run byte c
and the terminator Q are chosen per pattern by search (the pair maximising T at k = 500 over the
pattern's own alphabet).  Reported: T, T/n and the growth T(16k)/T(4k): ~4 is linear, ~16 quadratic.

    PCREC=build/pcrec python3 qwork.py ms_rows.tsv.gz OUTDIR  > qwork.txt
"""
import csv, gzip, os, re, subprocess, sys, concurrent.futures as cf

csv.field_size_limit(sys.maxsize)
HERE = os.path.dirname(os.path.abspath(__file__))
PCREC = os.environ.get("PCREC", "build/pcrec")
GT = "/usr/bin/gnutimeout"
REPO = os.environ.get("CORPUS", ".")
NICE = ["nice", "-n", "10"]
CFLAGS = ["-O0", "-g", "-fno-pie", "-no-pie", "-fsanitize=kernel-address", "--param",
          "asan-instrumentation-with-call-threshold=0", "--param", "asan-stack=0", "--param", "asan-globals=0",
          "-fno-builtin-memchr", "-fno-builtin-memrchr", "-fno-builtin-memcmp", "-fno-builtin-memmem",
          "-w", "-fcf-protection=none"]


def route(r):
    e, v, s = r["ENGINE"], r["VM_PREFILTER"], r["DFA_SCAN"]
    if e == "dfa":
        return ("dfa-attempt" if s == "attempt" else "dfa-" + s)
    return ("hybrid-" + s) if v == "hybrid" else "vm-only"


def build(r, wd):
    os.makedirs(wd, exist_ok=True)
    pat = (b"(?i)" if r["icase"] == "True" else b"") + bytes.fromhex(r["pattern_hex"])
    cmd = NICE + [GT, "40", PCREC, "-p", "rx", "--features", "all", "-o", wd + "/rx.c"] + \
        (["-e", "utf8"] if r["enc"] == "utf8" else []) + ["--pattern", pat]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        return None
    src = open(wd + "/rx.c").read()
    marker = "size_t scan_position = start;"
    attempts = marker in src
    if attempts:
        src = src.replace(marker, "size_t scan_position = (rx_ms_attempts++, start);")
        src = src.replace('#include "rx.h"', '#include "rx.h"\nunsigned long long rx_ms_attempts;', 1)
    open(wd + "/rx_i.c", "w").write(src)
    g = NICE + [GT, "-k", "2", "90", "gcc"] + CFLAGS + ["-I", wd, "-c", "-o", wd + "/a.o", wd + "/rx_i.c"]
    p = subprocess.run(g, capture_output=True)
    if p.returncode != 0:
        return None
    g = NICE + [GT, "-k", "2", "90", "gcc", "-O1", "-w", "-fno-pie", "-fno-builtin", "-I", wd, "-c", "-o", wd + "/d.o", HERE + "/qdrv.c"]
    p = subprocess.run(g, capture_output=True)
    if p.returncode != 0:
        return None
    p = subprocess.run(NICE + [GT, "60", "gcc", "-no-pie", "-o", wd + "/q", wd + "/a.o", wd + "/d.o"], capture_output=True)
    return wd + "/q" if p.returncode == 0 else None


def run(q, pre, run_b, k, suf):
    p = subprocess.run(NICE + [GT, "-k", "2", "60", q, pre.hex(), run_b.hex(), str(k), suf.hex()], capture_output=True)
    if p.returncode != 0:
        return None
    f = p.stdout.decode().split()
    return dict(n=int(f[0]), calls=int(f[1]), matches=int(f[2]), T=int(f[3]), att=int(f[4]))


def alpha(pat):
    s = {" ", "\t", "a", "0", "/", ".", "-", "_", "x", ",", ";", ":", "\n"}
    for ch in pat.decode("latin-1"):
        if ch.isalnum() or ch in " ./-_,;:#\"'[](){}<>=+*":
            s.add(ch)
    return sorted(s)


def study(r, wd):
    q = build(r, wd)
    if q is None:
        return dict(id=r["id"], err="build")
    pat = bytes.fromhex(r["pattern_hex"])
    best = None
    al = alpha(pat)
    for c in al[:24]:
        for t in ("Q", "\x01"):
            res = run(q, b"Q", c.encode("latin-1"), 500, t.encode())
            if res and (best is None or res["T"] > best[0]):
                best = (res["T"], c, t, res)
    if best is None:
        return dict(id=r["id"], err="run")
    _, c, t, _ = best
    out = dict(id=r["id"], c=c, t=t, mix=r["mix"], route=route(r), pattern=pat.decode("latin-1"))
    for shape, pre, suf in (("internal", b"Q", t.encode()), ("trailing", b"Q", b""), ("whole", b"", b"")):
        out[shape] = {k: run(q, pre, c.encode("latin-1"), k, suf) for k in (1000, 4000, 16000)}
    return out


def fmt(o):
    if "err" in o:
        return "%-44s ERROR %s" % (o["id"][:44], o["err"])
    lines = ["%-9s %-7s %-14s %s   run=%r term=%r" % (o["mix"], "", o["route"], o["pattern"][:50].replace("\n", "\\n"), o["c"], o["t"])]
    for shape in ("internal", "trailing", "whole"):
        d = o[shape]
        if not all(d.values()):
            lines.append("    %-9s (a run failed)" % shape); continue
        g = d[16000]["T"] / max(d[4000]["T"], 1)
        lines.append("    %-9s T(1k)=%-10d T(4k)=%-11d T(16k)=%-12d growth16k/4k=%5.2f  T/n@16k=%8.1f  calls@16k=%d  attempts@16k=%s" % (
            shape, d[1000]["T"], d[4000]["T"], d[16000]["T"], g, d[16000]["T"] / d[16000]["n"], d[16000]["calls"],
            d[16000]["att"] if d[16000]["att"] >= 0 else "n/a"))
    return "\n".join(lines)


def main():
    rows = list(csv.DictReader(gzip.open(sys.argv[1], "rt"), delimiter="\t"))
    outdir = sys.argv[2]
    ok = [r for r in rows if r["status"] == "ok" and not r["refused"] and r["pop"] != "planted"]
    risk = [r for r in ok if r["lu_E"] == "1" and route(r) in ("dfa-attempt", "hybrid-attempt", "vm-only", "hybrid-unanchored", "dfa-unanchored")
            and r["adv"] != "True" and route(r) != "dfa-unanchored"]
    ctrl = [r for r in ok if r["lu_E"] == "1" and route(r) in ("dfa-rev-end", "hybrid-rev-end") and r["adv"] != "True"][:6]
    print("QUADRATIC-RISK population measured: %d patterns (lu_E, route tries each start, non-D27);  controls (rev-end routes): %d" % (len(risk), len(ctrl)))
    print("work = subject-byte loads of a whole find-all (qdrv.c); growth16k/4k ~ 4 linear, ~ 16 quadratic\n")
    jobs = [(r, os.path.join(outdir, "w%03d" % i)) for i, r in enumerate(risk + ctrl)]
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        res = list(ex.map(lambda a: study(*a), jobs))
    print("---- RISK ----")
    for o in res[:len(risk)]:
        print(fmt(o))
    print("\n---- CONTROLS (rev-end routes: the walk starts at n) ----")
    for o in res[len(risk):]:
        print(fmt(o))


if __name__ == "__main__":
    main()

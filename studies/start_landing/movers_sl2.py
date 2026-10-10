#!/usr/bin/env python3
"""SL2's MOVERS-EQUAL-CENSUS check (lane slbuild; start_landing.md §7.1 SL2
(a)): every population compile on the PARENT build (SL1) and the CHILD build
(SL2). The PREDICTION is the design's first-match RECOVER rule applied to the
PARENT's own outputs, which share no code with the child's new rows: the
parent's `--emit-facts` (`width`, `land_char`) and its stamps (`RX_DFA_START`
reverse-pass, `RX_DFA_PREFILTER`). The child's `RX_DFA_START` must equal the
prediction on every compile, and a compile whose prediction is unchanged must
be byte-identical apart from the abi stamp lines.

    movers_sl2.py PARENT CHILD POP.tsv... > movers.tsv   (summary on stderr)
"""
import os, re, subprocess, sys, tempfile, threading
from concurrent.futures import ThreadPoolExecutor

PAR, CHI = sys.argv[1], sys.argv[2]
TMP = tempfile.mkdtemp(prefix="mov.", dir=os.environ.get("TMPDIR", "."))


def esc(b):
    o = []
    for c in b:
        if c == 0x5c: o.append("\\\\")
        elif c == 0x22: o.append('\\"')
        elif 0x20 <= c < 0x7f: o.append(chr(c))
        else: o.append("\\x%02x" % c)
    return "".join(o)


def stamps(path):
    d = {}
    for l in open(path, encoding="latin-1"):
        m = re.match(r'#define RX_(DFA_START|DFA_SCAN|DFA_PREFILTER|ENGINE) "([^"]*)"', l)
        if m: d[m.group(1)] = m.group(2)
    return d


def norm(path):
    """the artifact minus the abi digits (the one deliberate byte the SL2
    event moves on every artifact)."""
    t = open(path, encoding="latin-1").read()
    t = re.sub(r"abi[ :]*7[34]", "abi:N", t)
    t = re.sub(r"PCREC_RX_ABI_7[34]", "PCREC_RX_ABI_N", t)
    t = re.sub(r"(PCREC_ARTIFACT_ABI|\.abi|_ABI)( *=? *)7[34]", r"\1\2N", t)
    return t


def one(job):
    pid, enc, icase, pat, cfg = job
    base = ["--features", "all"]
    if enc == "utf8": base += ["-e", "utf8"]
    if icase == "1": base.append("-i")
    if cfg == "nocaps": base.append("--no-captures")
    pe = ["--pattern-esc", "--pattern", "\"" + esc(pat) + "\""]
    tid = "%d" % threading.get_ident()
    pa, ca = os.path.join(TMP, "p", tid, "rx.c"), os.path.join(TMP, "c", tid, "rx.c")
    os.makedirs(os.path.dirname(pa), exist_ok=True); os.makedirs(os.path.dirname(ca), exist_ok=True)
    try:
        r1 = subprocess.run([PAR] + base + ["-p", "rx", "-o", pa] + pe, capture_output=True, timeout=300)
        r2 = subprocess.run([CHI] + base + ["-p", "rx", "-o", ca] + pe, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return [pid, cfg, enc, "timeout"]
    if r1.returncode or r2.returncode:
        return [pid, cfg, enc, "refused" if r1.returncode == r2.returncode else "ASYM"]
    sp, sc = stamps(pa), stamps(ca)
    same = norm(pa) == norm(ca)
    if sp.get("DFA_START") != "reverse-pass" or sp.get("DFA_SCAN") != "unanchored":
        pred = sp.get("DFA_START", "-")
        why = "unchanged"
    else:
        q = subprocess.run([PAR] + base + ["--emit-facts"] + pe, capture_output=True, timeout=300)
        f = {}
        for l in q.stdout.decode("latin-1").split("\n"):
            x = l.split("\t")
            if len(x) >= 8 and x[1] in ("land_char", "width"): f[x[1]] = x[6]
        w = f.get("width", "none")
        m = re.match(r"\[(\d+),(\d+)\]$", w)
        if m and m.group(1) == m.group(2):
            pred, why = "end-minus-width", "W=" + m.group(1)
        elif f.get("land_char", "none").startswith("one-char") and sp.get("DFA_PREFILTER", "none") != "none":
            pred, why = "landing", f["land_char"]
        else:
            pred, why = "reverse-pass", "declined"
    got = sc.get("DFA_START", "-")
    verdict = "ok" if got == pred else "MISPREDICT"
    if verdict == "ok" and pred == sp.get("DFA_START", "-") and not same:
        verdict = "BYTEMOVE"
    if verdict == "ok" and pred != sp.get("DFA_START", "-") and same:
        verdict = "NOMOVE"
    return [pid, cfg, enc, verdict, sp.get("DFA_START", "-"), got, pred, why, sp.get("ENGINE", "-")]


jobs, seen = [], set()
for pop in sys.argv[3:]:
    for line in open(pop):
        f = line.rstrip("\n").split("\t")
        if f[0] == "pid": continue
        key = (f[0], f[2], f[3], f[4])
        if key in seen: continue
        seen.add(key)
        for cfg in ("default", "nocaps"):
            jobs.append((f[0], f[2], f[3], bytes.fromhex(f[4]), cfg))
tally = {}
print("pid\tconfig\tenc\tverdict\tparent\tchild\tpredicted\twhy\tengine")
with ThreadPoolExecutor(int(os.environ.get("JOBS", "8"))) as ex:
    for row in ex.map(one, jobs):
        k = row[3] if row[3] != "ok" else "ok:%s->%s" % (row[4], row[5])
        tally[k] = tally.get(k, 0) + 1
        print("\t".join(row), flush=True)
print("MOVERS_SL2 compiles=%d %s" % (len(jobs), " ".join("%s=%d" % kv for kv in sorted(tally.items()))),
      file=sys.stderr)

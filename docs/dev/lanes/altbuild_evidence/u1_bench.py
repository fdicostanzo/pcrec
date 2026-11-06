"""u1_bench.py BASE_PCREC STAGE_PCREC BENCH_UTF8_PATTERNS OUT [--jobs N] -- Gate U1
on the bench/utf8 population (docs/design/alt_normal_form.md §5 stage 1;
lane altbuild2, 2026-11-06). BASE is the base with only its abi digit bumped
(B0's REF), STAGE the stage 1+2p build: U1 is stage 1's gate, and 2p is inert.

OBSERVED, per pattern, per observable (U1's table): `run` (the utf8
`req_whole_run` facts row), `tables` (each machine's next-state entry count,
auto route; U3: no machine grows), `vmbytes`/`islands`/`rungs` (the VM route
under `-fno-cls-kit`, where wide classes are lowered to bytes), `refused`
(either compile's rc).

PREDICTED, by the design's construct clause, not by pcrec: a pattern moves
only if it holds a class whose UTF-8 split has more than one box, which in
this population is any of: `.`, a negated class, `\\p`/`\\P`, `\\W` `\\D`
`\\S` (and their ucp positives), a bracket class or range reaching above
0x7F, or a caseless non-ASCII letter (a fold orbit). The ASCII clause: a
pattern with none of them is predicted a non-mover on EVERY observable, and
any move there is a FINDING. A predicted pattern that does not move is
listed (the observable can be blind to a merge: a one-box split, a kit-
routed class); the per-observable direction is checked where the design
states one: `tables` and `vmbytes` never grow, `islands` only fall 1 -> 0,
refusals only retire. This is a coarser model than u1_folds.py's (no
box arithmetic for properties: that would need the UCD tables pcrec
itself reads), stated as such in the report."""
import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

WIDE = re.compile(rb"""(?<!\\)\.|\[\^|\\[pP]|\\[WDS]""")
HIGH = re.compile(rb"""[\x80-\xff]|\\x\{[0-9a-fA-F]{3,}\}|\\x\{?[89a-fA-F][0-9a-fA-F]""")
UCP = re.compile(rb"\(\*UCP\)|\(\?[a-zA-Z]*u")

def brackets(pat):
    """The text of each bracket class (escapes honoured, a leading `]` literal)."""
    out, i = [], 0
    while i < len(pat):
        c = pat[i:i + 1]
        if c == b"\\": i += 2; continue
        if c == b"[":
            j = i + 1
            if pat[j:j + 1] == b"^": j += 1
            if pat[j:j + 1] == b"]": j += 1
            while j < len(pat) and pat[j:j + 1] != b"]":
                j += 2 if pat[j:j + 1] == b"\\" else 1
            out.append(pat[i:j + 1]); i = j + 1; continue
        i += 1
    return out

def predicted(pat):
    """A class with a multi-box UTF-8 split: a wide construct, a bracket class
    reaching above 0x7F, or a non-ASCII letter under caseless matching (its
    fold orbit). A non-ASCII LITERAL alone is one box and predicts nothing."""
    if WIDE.search(pat): return True
    if any(HIGH.search(b) for b in brackets(pat)): return True
    if re.search(rb"\(\?[a-zA-Z]*i", pat) and HIGH.search(pat): return True
    return bool(UCP.search(pat) and re.search(rb"\\[wds]", pat))

def run(pcrec, pat, extra):
    try:
        r = subprocess.run([pcrec, "-p", "rx", "-e", "utf8", "--features", "all"] + extra
                           + ["-o", "-", "--pattern", pat], capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    return None if r.returncode else r.stdout.decode("latin-1")

def facts(pcrec, pat):
    try:
        r = subprocess.run([pcrec, "-p", "rx", "--features", "all", "--emit-facts=utf8",
                            "--pattern", pat], capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return "?"
    for line in r.stdout.decode("latin-1").splitlines():
        f = line.split("\t")
        if len(f) > 6 and f[1] == "req_whole_run": return f[6]
    return "-"

def obs(pcrec, pat):
    a = run(pcrec, pat, [])
    v = run(pcrec, pat, ["--engine=vm", "-fno-cls-kit"])
    o = {"run": facts(pcrec, pat), "refused": (a is None, v is None)}
    o["tables"] = dict((m.group(1), int(m.group(2))) for m in
                       re.finditer(r"rx_(\w+?)_next_state\[(\d+)\]", a or ""))
    for k, n in (("vmbytes", "VM_PROGRAM_BYTES"), ("islands", "VM_ALT_ISLANDS"), ("rungs", "VM_RUNGS")):
        m = re.search(r"#define RX_%s\s+(\S+)" % n, v or "")
        o[k] = m.group(1) if m else "-"
    return o

def one(args):
    base, stage, name, pat = args
    b, s = obs(base, pat), obs(stage, pat)
    moved = [k for k in ("run", "tables", "vmbytes", "islands", "rungs", "refused") if b[k] != s[k]]
    bad = []
    for k, x in s["tables"].items():
        if k in b["tables"] and x > b["tables"][k]: bad.append("U3 growth %s %d->%d" % (k, b["tables"][k], x))
    if "vmbytes" in moved and "-" not in (b["vmbytes"], s["vmbytes"]) and int(s["vmbytes"].rstrip("ULL")) > int(b["vmbytes"].rstrip("ULL")):
        bad.append("vmbytes grew")
    if "islands" in moved and not (b["islands"] == "1" and s["islands"] == "0"): bad.append("islands %s->%s" % (b["islands"], s["islands"]))
    if "refused" in moved and (s["refused"][0] and not b["refused"][0] or s["refused"][1] and not b["refused"][1]):
        bad.append("NEW refusal")
    return name, pat, predicted(pat), moved, bad, b, s

def main():
    a = sys.argv[1:]
    jobs = 8
    if "--jobs" in a:
        i = a.index("--jobs"); jobs = int(a[i + 1]); del a[i:i + 2]
    base, stage, d, out = a
    pats = []
    for f in sorted(os.listdir(d)):
        if f.endswith(".rx"):
            for i, line in enumerate(open(os.path.join(d, f), "rb").read().split(b"\n")):
                if line: pats.append((f[:-3] + (":%d" % (i + 1) if i else ""), line))
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(one, [(base, stage, n, p) for n, p in pats]))
    findings = 0
    with open(os.path.join(out, "u1_bench.tsv"), "w") as f:
        f.write("pattern\tpredicted\tmoved\tverdict\tdetail\n")
        for name, pat, pred, moved, bad, b, s in res:
            if bad: v = "FINDING"
            elif moved and not pred: v = "UNPREDICTED-MOVER"
            elif moved: v = "predicted-mover"
            elif pred: v = "predicted-not-moved"
            else: v = "non-mover"
            if v in ("FINDING", "UNPREDICTED-MOVER"): findings += 1
            det = "; ".join(bad + ["%s %s->%s" % (k, b[k], s[k]) for k in moved])
            f.write("%s\t%s\t%s\t%s\t%s\n" % (name, pred, ",".join(moved) or "-", v, det))
    import collections
    c = collections.Counter()
    for name, pat, pred, moved, bad, b, s in res:
        for k in moved: c[k] += 1
    print("population: %d bench/utf8 patterns; predicted (wide construct): %d; moved: %d; per observable: %s"
          % (len(res), sum(r[2] for r in res), sum(1 for r in res if r[3]), dict(c)))
    print("refused on both builds (either route): %d" % sum(1 for r in res if r[5]["refused"] == r[6]["refused"] and any(r[5]["refused"])))
    print("findings (unpredicted mover, growth, island rise, new refusal): %d" % findings)
    if not res: print("FLOOR: empty population"); sys.exit(1)
    sys.exit(1 if findings else 0)

main()

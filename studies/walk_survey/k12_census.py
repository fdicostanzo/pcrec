#!/usr/bin/env python3
"""walk_survey: K12's static population (inner landmark).

    k12_census.py PCREC POP.tsv > OUT.tsv

For every pattern of a population (pop_bench.py / pop_corpus.py rows, one per
pattern), asks `pcrec --emit-facts` (default config) for the route stamps,
`start_set` and the necessary landmark (`req_byte`, else the first byte of
`req_run`'s pick, both case variants when masked). A pattern is an
INNER-LANDMARK candidate when it is on the DFA route or a VM hybrid, has a
landmark, and the start set is at least 16x as wide as the landmark (the
forward machine then steps most text a memchr for the landmark would skip;
`landmark_in_start` says whether the landmark is itself a start byte). Counted, not timed; the bench's measured m_gap prices it.
"""
import subprocess, sys

PCREC, POP = sys.argv[1], sys.argv[2]


def esc(b):
    o = []
    for c in b:
        if c == 0x5c: o.append("\\\\")
        elif c == 0x22: o.append('\\"')
        elif 0x20 <= c < 0x7f: o.append(chr(c))
        else: o.append("\\x%02x" % c)
    return '"' + "".join(o) + '"'


seen = {}
for ln in open(POP).read().split("\n")[1:]:
    f = ln.split("\t")
    if len(f) >= 5 and f[0] not in seen:
        seen[f[0]] = (f[2], f[3] == "1", bytes.fromhex(f[4]))
print("pid\tenc\tengine\tvm_prefilter\tdfa_scan\tstart_set_n\tlandmark\tlandmark_in_start\tk12")
for pid, (enc, ic, pat) in seen.items():
    args = [PCREC, "--emit-facts", "--features", "all"] + (["-e", "utf8"] if enc == "utf8" else []) + \
           (["-i"] if ic else []) + ["--pattern-esc", "--pattern", esc(pat)]
    try:
        r = subprocess.run(args, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        continue
    if r.returncode != 0:
        continue
    fa, st = {}, {}
    for l in r.stdout.decode("utf8", "replace").split("\n"):
        x = l.split("\t")
        if len(x) >= 7 and x[1] in ("start_set", "req_byte", "req_run"):
            fa[x[1]] = x[6] if x[4] != "declined" else "none"
        elif len(x) == 3 and x[1].startswith("RX_"):
            st[x[1]] = x[2].strip('"')
    ss = fa.get("start_set", "")
    bits = set()
    if ":" in ss:
        h = bytes.fromhex(ss.split(":", 1)[1])
        bits = {i for i in range(256) if h[i // 8] >> (i % 8) & 1}
    lm = set()
    rb = fa.get("req_byte", "none")
    rr = fa.get("req_run", "none")
    if rb not in ("none", "") and rb.isdigit():
        lm = {int(rb)}
    elif rr not in ("none", "") and "@" in rr:
        run, rest = rr.split("@", 1)
        b0 = int(run[:2], 16)
        lm = {b0}
        if "/" in rest:
            m0 = int(rest.split("/", 1)[1][:2], 16)
            lm.add(b0 | (~m0 & 0xff))
            lm.add(b0 & m0)
    eng = st.get("RX_ENGINE", "")
    vmp = st.get("RX_VM_PREFILTER", "")
    inner = bool(lm) and not (lm & bits)
    # a landmark at least 16x narrower than the start set: the forward
    # machine steps most text a memchr for the landmark would skip
    k12 = bool(lm) and len(bits) >= 16 * len(lm) and (eng == "dfa" or vmp == "hybrid")
    print("%s\t%s\t%s\t%s\t%s\t%d\t%s\t%s\t%d" % (pid, enc, eng, vmp, st.get("RX_DFA_SCAN", ""), len(bits),
          ",".join(str(b) for b in sorted(lm)) or "-", "no" if inner else ("yes" if lm else "-"), int(k12)))

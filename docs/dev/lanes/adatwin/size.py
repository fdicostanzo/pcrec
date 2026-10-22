#!/usr/bin/env python3
"""adatwin/size.py OUT -- object size per (cell, arm), compile-only (lane adatwin).

Per cell and arm, from OUT/bin/<cell>/<arm>/art.c compiled with the slot's own flags (gcc -O2, as build.sh):
  text, rodata   `size -A` of art.o (the whole artifact object)
  site_fn        nm -S size of the function the candidate site is inlined into (rx_search, or rx_search_run on the
                 VM-hybrid site; the largest of the two that exists)
  producer       nm -S size of <stem>__next_candidate alone, from a second compile of the same art.c with
                 __attribute__((noinline)) on it (its helpers inline into it, as they do into the site); walk: 0
  c_bytes        emitted C bytes of the producer: the cursor struct through the end of next_candidate, minus the
                 mask/member helpers every arm shares (V1's text); for the ADAPT arms the walk table they copy in is
                 inside that span; walk: the bytes of its one skip-loop line
Writes OUT/size.tsv and prints per-arm sums and deltas vs walk and vs V1 (markdown).
"""
import os
import re
import subprocess
import sys

ARMS = ["walk", "V1", "M64", "OBS", "ADAPT", "ADAPTC", "ADAPT1C"]


def sec(obj):
    out = subprocess.run(["size", "-A", obj], capture_output=True, text=True, check=True).stdout
    d = {}
    for ln in out.splitlines():
        f = ln.split()
        if len(f) >= 2 and f[0].startswith("."):
            d[f[0]] = d.get(f[0], 0) + int(f[1])
    return d.get(".text", 0), sum(v for k, v in d.items() if k.startswith(".rodata"))


def syms(obj):
    out = subprocess.run(["nm", "-S", obj], capture_output=True, text=True, check=True).stdout
    d = {}
    for ln in out.splitlines():
        f = ln.split()
        if len(f) == 4 and f[2] in "tT":
            d[f[3]] = int(f[1], 16)
    return d


def c_bytes(src, arm):
    t = open(src).read()
    if arm == "walk":
        m = re.search(r"^.*!\w+\[subject\[scan_position\]\]\) scan_position\+\+;\n", t, re.M)
        return len(m.group(0))
    st = re.search(r"^struct (\w+)__c \{$", t, re.M)
    stem = st.group(1)
    pat = re.compile(r"^struct %s__c \{\n.*?^static inline size_t %s__next_candidate\(.*?^\}\n" % (stem, stem), re.S | re.M)
    m = pat.search(t)
    if not m:   # the adaptive arms place helpers/tables before the struct: start at the first helper after member()
        mem = re.search(r"^static inline int %s__member\(.*?^\}\n" % stem, t, re.S | re.M)
        end = re.search(r"^static inline size_t %s__next_candidate\(.*?^\}\n" % stem, t, re.S | re.M)
        span = t[mem.end():end.end()]
    else:
        span = m.group(0)
    keep = re.compile(r"^static inline (unsigned long long %s__mask|int %s__member)\(.*?^\}\n" % (stem, stem), re.S | re.M)
    return len(span) - sum(len(k.group(0)) for k in keep.finditer(span))


def main():
    out = sys.argv[1]
    rows = []
    for c in sorted(os.listdir(os.path.join(out, "bin"))):
        for a in ARMS:
            d = os.path.join(out, "bin", c, a)
            src = os.path.join(d, "art.c")
            if not os.path.exists(src):
                continue
            obj = os.path.join(d, "art.size.o")
            subprocess.run(["gcc", "-O2", "-I" + d, "-I" + os.path.join(out, "lib"), "-c", src, "-o", obj], check=True)
            text, ro = sec(obj)
            s = syms(obj)
            site = max(s.get("rx_search", 0), s.get("rx_search_run", 0))
            prod = 0
            if a != "walk":
                t = open(src).read()
                ni = re.sub(r"^static inline size_t (\w+__next_candidate)\(", r"__attribute__((noinline)) static size_t \1(", t, flags=re.M)
                nsrc = os.path.join(d, "art.ni.c")
                open(nsrc, "w").write(ni)
                nobj = os.path.join(d, "art.ni.o")
                subprocess.run(["gcc", "-O2", "-I" + d, "-I" + os.path.join(out, "lib"), "-c", nsrc, "-o", nobj], check=True)
                prod = sum(v for k, v in syms(nobj).items() if k.endswith("__next_candidate"))
            rows.append((c, a, text, ro, site, prod, c_bytes(src, a)))
    with open(os.path.join(out, "size.tsv"), "w") as f:
        f.write("cell\tarm\ttext\trodata\tsite_fn\tproducer\tc_bytes\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    cells = sorted({r[0] for r in rows})
    by = {(r[0], r[1]): r for r in rows}
    print("| cell | " + " | ".join("%s text/ro/prod/C" % a for a in ARMS) + " |")
    print("|---|" + "---|" * len(ARMS))
    for c in cells:
        print("| %s | " % c + " | ".join(("%d/%d/%d/%d" % (by[(c, a)][2], by[(c, a)][3], by[(c, a)][5], by[(c, a)][6])) if (c, a) in by else "-" for a in ARMS) + " |")
    print()
    print("| arm | text sum | rodata sum | producer sum | C bytes sum | text vs walk | text vs V1 | producer vs V1 | text+ro vs V1 |")
    print("|---|---|---|---|---|---|---|---|---|")
    tot = {a: [sum(by[(c, a)][i] for c in cells if (c, a) in by) for i in range(2, 7)] for a in ARMS}
    for a in ARMS:
        t = tot[a]
        print("| %s | %d | %d | %d | %d | %+d (%+.0f%%) | %+d (%+.0f%%) | %+d | %+d |" % (
            a, t[0], t[1], t[3], t[4], t[0] - tot["walk"][0], 100.0 * (t[0] - tot["walk"][0]) / tot["walk"][0],
            t[0] - tot["V1"][0], 100.0 * (t[0] - tot["V1"][0]) / tot["V1"][0], t[3] - tot["V1"][3],
            t[0] + t[1] - tot["V1"][0] - tot["V1"][1]))


if __name__ == "__main__":
    main()
